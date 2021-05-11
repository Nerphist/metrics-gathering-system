# Generated by Django 3.1.4 on 2021-05-11 17:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tariff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(
                    choices=[('Gas', 'Gas'), ('Water', 'Water'), ('Electricity', 'Electricity'), ('Heat', 'Heat')],
                    max_length=255)),
                ('notes', models.CharField(max_length=255)),
                ('file', models.FileField(default=None, null=True, upload_to='')),
                ('enacted_since', models.DateTimeField(default=None, null=True)),
                ('commercial_price', models.DecimalField(decimal_places=2, default=None, max_digits=30, null=True)),
                ('reduced_price', models.DecimalField(decimal_places=2, default=None, max_digits=30, null=True)),
                ('residential_price', models.DecimalField(decimal_places=2, default=None, max_digits=30, null=True)),
            ],
            options={
                'ordering': ['pk'],
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='supplycontract',
            name='name',
        ),
        migrations.AlterField(
            model_name='supplycontract',
            name='type',
            field=models.CharField(
                choices=[('Gas', 'Gas'), ('Water', 'Water'), ('Electricity', 'Electricity'), ('Heat', 'Heat')],
                max_length=255),
        ),
    ]