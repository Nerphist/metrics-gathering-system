# Generated by Django 3.1.4 on 2021-04-24 14:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_index_change'),
        ('permissions', '0001_permissions'),
    ]

    operations = [
        migrations.AlterIndexTogether(
            name='permissiongroup',
            index_together={('user_group_id', 'entity_type', 'entity_id')},
        ),
    ]