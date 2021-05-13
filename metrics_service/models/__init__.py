import enum


class PermissionSet(enum.Enum):
    LocationRead = 'LocationRead'
    LocationEdit = 'LocationEdit'
    BuildingTypeRead = 'BuildingTypeRead'
    BuildingTypeEdit = 'BuildingTypeEdit'
    BuildingRead = 'BuildingRead'
    BuildingEdit = 'BuildingEdit'
    FloorRead = 'FloorRead'
    FloorEdit = 'FloorEdit'
    RoomRead = 'RoomRead'
    RoomEdit = 'RoomEdit'
    MeterRead = 'MeterRead'
    MeterEdit = 'MeterEdit'
    MeterSnapshotRead = 'MeterSnapshotRead'
    MeterSnapshotEdit = 'MeterSnapshotEdit'
