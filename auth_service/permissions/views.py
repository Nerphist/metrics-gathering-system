from itertools import groupby
from typing import Set, Dict, List

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_service.settings import ADMIN_GROUP_NAME
from permissions.metrics_api import get_structure
from permissions.models import PermissionGroup
from permissions.permissions import is_admin
from permissions.serializers import GetPermissionsRequestQuerySerializer, \
    AddPermissionsRequestSerializer, GetPermissionsResponseSerializer
from users.models import User, UserGroup


def _get_permissions_for_user_group(user_group, init_permissions=None) -> Dict[str, Dict[str, List[str]]]:
    if not init_permissions:
        init_permissions = {str(entity): {} for entity in PermissionGroup.EntityTypes.__members__}

    for permission_group in user_group.permission_groups.all():
        if permission_group.entity_id in init_permissions[permission_group.entity_type]:
            current_set = set(init_permissions[permission_group.entity_type][permission_group.entity_id])
            current_set.update(set(permission_group.permission_set))
            init_permissions[permission_group.entity_type][permission_group.entity_id] = list(current_set)
        else:
            init_permissions[permission_group.entity_type][
                permission_group.entity_id] = permission_group.permission_set

    return init_permissions


def make_permissions_tree(user: User, structure, for_add=False):
    children_dict = {
        PermissionGroup.EntityTypes.building.name: PermissionGroup.EntityTypes.floor.name,
        PermissionGroup.EntityTypes.floor.name: PermissionGroup.EntityTypes.room.name,
        PermissionGroup.EntityTypes.room.name: PermissionGroup.EntityTypes.device.name,
    }

    tree = {
        int(building_id): {
            'permissions': [],
            PermissionGroup.EntityTypes.floor.name: {int(floor_id): {
                'permissions': [],
                PermissionGroup.EntityTypes.room.name: {int(room_id): {
                    'permissions': [],
                    PermissionGroup.EntityTypes.device.name: {int(device_id): {
                        'permissions': [],
                    } for device_id in devices}
                } for room_id, devices in rooms.items()}
            } for floor_id, rooms in floors.items()}
        }
        for building_id, floors in structure.items()}

    if for_add:
        user_groups = user.controlled_groups.all()
    else:
        user_groups = user.user_groups.all()

    initial_permission_groups = [permission_group for user_group in user_groups for permission_group in
                                 user_group.permission_groups.all()]

    combined_permission_groups = []
    permission_groups_dict = groupby(initial_permission_groups, lambda x: (x.entity_id, x.entity_type))
    for key, group in permission_groups_dict:
        group = list(group)
        if len(group) == 1:
            combined_permission_groups.append(group[0])
        else:
            combined_permission_set = set()
            for permission in group:
                combined_permission_set.update(set(permission.permission_set))
            group[0].permission_set = list(combined_permission_set)
            combined_permission_groups.append(group[0])

    building_permissions = [permission_group for permission_group in combined_permission_groups if
                            permission_group.entity_type == PermissionGroup.EntityTypes.building.name]
    floor_permissions = [permission_group for permission_group in combined_permission_groups if
                         permission_group.entity_type == PermissionGroup.EntityTypes.floor.name]
    room_permissions = [permission_group for permission_group in combined_permission_groups if
                        permission_group.entity_type == PermissionGroup.EntityTypes.room.name]
    device_permissions = [permission_group for permission_group in combined_permission_groups if
                          permission_group.entity_type == PermissionGroup.EntityTypes.device.name]

    def _fill_for_children(entity_type: str, permission_set: List[str], sub_structure, sub_tree):
        children_type = children_dict[entity_type]
        if isinstance(sub_structure, dict):
            children_ids = [int(cid) for cid in sub_structure.keys()]
        else:
            children_ids = [int(cid) for cid in sub_structure]
        for cid in children_ids:
            existing_set_ = set(sub_tree[cid]['permissions'])
            new_set_ = set(permission_set)
            existing_set_.update(new_set_)
            sub_tree[cid].update({
                'permissions': list(existing_set_),
            })
            if children_type in children_dict:
                _fill_for_children(
                    children_type,
                    permission_set,
                    sub_structure[str(cid)],
                    sub_tree[cid][children_dict[children_type]]
                )

    for permission_group in building_permissions:
        existing_set = set(tree[permission_group.entity_id]['permissions'])
        new_set = set(permission_group.permission_set)
        existing_set.update(new_set)
        tree[permission_group.entity_id]['permissions'] = list(existing_set)
        sub_tree = tree[permission_group.entity_id][children_dict[permission_group.entity_type]]
        sub_structure = structure[str(permission_group.entity_id)]
        _fill_for_children(
            permission_group.entity_type,
            permission_group.permission_set,
            sub_structure,
            sub_tree
        )

    for permission_group in floor_permissions:
        floor_id = permission_group.entity_id
        needed_tree = None
        needed_structure = None
        for building_id, floors in tree.items():
            if floor_id in floors[PermissionGroup.EntityTypes.floor.name]:
                needed_tree = tree[building_id][PermissionGroup.EntityTypes.floor.name]
        for building_id, floors in structure.items():
            if str(floor_id) in floors:
                needed_structure = structure[building_id]
        needed_tree[permission_group.entity_id].update({
            'permissions': permission_group.permission_set
        })
        sub_tree = needed_tree[permission_group.entity_id][children_dict[permission_group.entity_type]]
        sub_structure = needed_structure[str(permission_group.entity_id)]
        _fill_for_children(
            permission_group.entity_type,
            permission_group.permission_set,
            sub_structure,
            sub_tree
        )

    for permission_group in room_permissions:
        room_id = permission_group.entity_id
        needed_tree = None
        needed_structure = None
        for building_id, floors in tree.items():
            for floor_id, rooms in floors[PermissionGroup.EntityTypes.floor.name].items():
                if room_id in rooms[PermissionGroup.EntityTypes.room.name]:
                    needed_tree = tree[building_id][PermissionGroup.EntityTypes.floor.name][floor_id][
                        PermissionGroup.EntityTypes.room.name]
        for building_id, floors in structure.items():
            for floor_id, rooms in floors.items():
                if str(room_id) in rooms:
                    needed_structure = structure[building_id][floor_id]
        needed_tree[permission_group.entity_id].update({
            'permissions': permission_group.permission_set,
        })
        sub_tree = needed_tree[permission_group.entity_id][children_dict[permission_group.entity_type]]
        sub_structure = needed_structure[str(permission_group.entity_id)]
        _fill_for_children(
            permission_group.entity_type,
            permission_group.permission_set,
            sub_structure,
            sub_tree
        )

    for permission_group in device_permissions:
        device_id = permission_group.entity_id
        needed_tree = None
        for building_id, floors in tree.items():
            for floor_id, rooms in floors[PermissionGroup.EntityTypes.floor.name].items():
                for room_id, devices in rooms[PermissionGroup.EntityTypes.room.name].items():
                    if device_id in devices[PermissionGroup.EntityTypes.device.name]:
                        needed_tree = tree[building_id][PermissionGroup.EntityTypes.floor.name][floor_id][
                            PermissionGroup.EntityTypes.room.name][room_id][PermissionGroup.EntityTypes.device.name][
                            device_id]
        needed_tree[permission_group.entity_id].update({
            'permissions': permission_group.permission_set,
        })

    return tree


def _can_change_permissions(user: User, entity_id: int, entity_type: str, action_set: Set[str], structure):
    if is_admin(user):
        return True

    permission_tree = make_permissions_tree(user, structure, for_add=True)

    if entity_type == 'building':
        permissions = permission_tree[entity_id]['permissions']
        if action_set.issubset(set(permissions)):
            return True

    elif entity_type == 'floor':
        for _, building in permission_tree.items():
            for floor_id, floor in building['floor'].items():
                if floor_id == entity_id:
                    permissions = floor['permissions']
                    if action_set.issubset(set(permissions)):
                        return True

    elif entity_type == 'room':
        for _, building in permission_tree.items():
            for _, floor in building['floor'].items():
                for room_id, room in floor['room'].items():
                    if room_id == entity_id:
                        permissions = room['permissions']
                        if action_set.issubset(set(permissions)):
                            return True

    elif entity_type == 'device':
        for _, building in permission_tree.items():
            for _, floor in building['floor'].items():
                for _, room in floor['room'].items():
                    for device_id, device in room['device'].items():
                        if device_id == entity_id:
                            permissions = device['permissions']
                            if action_set.issubset(set(permissions)):
                                return True

    return False


@permission_classes([IsAuthenticated])
class PermissionsListView(APIView):

    @swagger_auto_schema(query_serializer=GetPermissionsRequestQuerySerializer)
    def get(self, request: Request, *args, **kwargs):
        if user_id := request.query_params.get('user_id'):
            user = User.objects.get(id=user_id)
        else:
            user = request.user

        structure = get_structure()
        permissions = make_permissions_tree(user, structure)

        return Response(data={'permissions': permissions, 'is_admin': is_admin(user)}, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=AddPermissionsRequestSerializer,
                         responses={'200': GetPermissionsResponseSerializer})
    def put(self, request: Request, *args, **kwargs):
        serializer = AddPermissionsRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_set = set(serializer.validated_data.get('actions'))
        if not action_set.issubset({str(m) for m in PermissionGroup.Action.__members__}):
            return Response(data={'detail': 'Actions are invalid'}, status=status.HTTP_400_BAD_REQUEST)

        structure = get_structure()

        structure_by_type = {str(entity): [] for entity in PermissionGroup.EntityTypes.__members__}
        for building_id, floors in structure.items():
            structure_by_type[PermissionGroup.EntityTypes.building.name].append(int(building_id))
            for floor_id, rooms in floors.items():
                structure_by_type[PermissionGroup.EntityTypes.floor.name].append(int(floor_id))
                for room_id, devices in rooms.items():
                    structure_by_type[PermissionGroup.EntityTypes.room.name].append(int(room_id))
                    structure_by_type[PermissionGroup.EntityTypes.device.name].extend(devices)

        if serializer.validated_data.get('entity_id') not in \
                structure_by_type[serializer.validated_data.get('entity_type')]:
            return Response(data={'detail': 'Entity does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        user_group: UserGroup = UserGroup.objects.filter(id=serializer.validated_data.get('user_group_id')).first()
        if not user_group:
            return Response(data={'detail': 'User group not found'}, status=status.HTTP_404_NOT_FOUND)

        if user_group.name == ADMIN_GROUP_NAME:
            return Response(data={'detail': 'Cannot change permissions of admin group'},
                            status=status.HTTP_400_BAD_REQUEST)

        entity_id = serializer.validated_data.get('entity_id')
        entity_type = serializer.validated_data.get('entity_type')

        permission: PermissionGroup = user_group.permission_groups.get_or_create(entity_id=entity_id,
                                                                                 entity_type=entity_type)[0]

        if _can_change_permissions(request.user, entity_type, entity_id, action_set, structure):
            permission.permission_set = list(action_set)
            permission.save()

            return Response(data=_get_permissions_for_user_group(user_group), status=status.HTTP_200_OK)
        else:
            return Response(
                data={'detail': 'User is not allowed to change these action permissions to this entity'},
                status=status.HTTP_403_FORBIDDEN)
