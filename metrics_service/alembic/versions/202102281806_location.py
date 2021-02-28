"""location

Revision ID: 7948a47abb4a
Revises: 
Create Date: 2021-02-28 18:06:48.467371

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
from sqlalchemy import UniqueConstraint

revision = '7948a47abb4a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('locations',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('longitude', sa.String(length=255), nullable=True),
                    sa.Column('latitude', sa.String(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name'),
                    UniqueConstraint('longitude', 'latitude', name='_coordinates_uc')
                    )
    op.create_table('buildings',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('location_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('building_floors',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('number', sa.Integer(), nullable=True),
                    sa.Column('building_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['building_id'], ['buildings.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    UniqueConstraint('number', 'building_id', name='_building_floor_number_uc')
                    )
    op.create_table('building_floor_rooms',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('floor_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['floor_id'], ['building_floors.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    UniqueConstraint('name', 'floor_id', name='_floor_room_name_uc')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('_floor_room_name_uc', 'building_floor_rooms', type_='unique')
    op.drop_constraint('_building_floor_number_uc', 'building_floors', type_='unique')
    op.drop_constraint('_coordinates_uc', 'locations', type_='unique')
    op.drop_table('building_floor_rooms')
    op.drop_table('building_floors')
    op.drop_table('buildings')
    op.drop_table('locations')
    # ### end Alembic commands ###
