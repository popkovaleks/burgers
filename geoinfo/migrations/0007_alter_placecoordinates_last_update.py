# Generated by Django 3.2.15 on 2022-12-04 10:00

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0006_alter_placecoordinates_last_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placecoordinates',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 4, 10, 0, 53, 368834, tzinfo=utc)),
        ),
    ]