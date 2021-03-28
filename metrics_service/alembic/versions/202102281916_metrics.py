"""metrics

Revision ID: 6ce6a6ab9cd0
Revises: 7948a47abb4a
Create Date: 2021-02-28 19:16:17.101300

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '6ce6a6ab9cd0'
down_revision = '7948a47abb4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('devices',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('serial', sa.String(length=255), nullable=True),
                    sa.Column('model_number', sa.String(length=255), nullable=True),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('description', sa.String(length=255), nullable=True),
                    sa.Column('secret_key', sa.String(length=63), nullable=True, unique=True),
                    sa.Column('recognition_key', sa.String(length=63), nullable=True, unique=True),
                    sa.Column('manufacture_date', sa.DateTime(), nullable=True),
                    sa.Column('type', sa.String(length=255), nullable=True),
                    sa.Column('room_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['room_id'], ['building_floor_rooms.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('serial')
                    )
    op.create_index(op.f('ix_devices_secret_key'), 'devices', ['secret_key'], unique=True)
    op.create_index(op.f('ix_devices_recognition_key'), 'devices', ['recognition_key'], unique=True)
    op.create_table('meters',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('device_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('device_id')
                    )
    op.create_table('readings',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('date', sa.DateTime(), nullable=True),
                    sa.Column('type', sa.String(length=255), nullable=True),
                    sa.Column('value', sa.String(length=255), nullable=True),
                    sa.Column('device_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('sensors',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('firmware_information', sa.String(length=255), nullable=True),
                    sa.Column('device_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('device_id')
                    )
    op.create_table('meter_sensor_binding',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('meter_id', sa.Integer(), nullable=True),
                    sa.Column('sensor_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['meter_id'], ['meters.id'], ),
                    sa.ForeignKeyConstraint(['sensor_id'], ['sensors.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('sensor_id', 'meter_id', name='_sensor_meter_uc')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('meter_sensor_binding')
    op.drop_table('sensors')
    op.drop_table('readings')
    op.drop_table('meters')
    op.drop_table('devices')
    # ### end Alembic commands ###
