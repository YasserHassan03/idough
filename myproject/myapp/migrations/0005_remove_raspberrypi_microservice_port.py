# Generated by Django 5.0.2 on 2024-02-14 01:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_raspberrypi_start_alter_raspberrypi_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='raspberrypi',
            name='microservice_port',
        ),
    ]