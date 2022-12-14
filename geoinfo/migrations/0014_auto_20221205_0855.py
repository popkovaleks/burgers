# Generated by Django 3.2.15 on 2022-12-05 08:55

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0013_alter_placecoordinates_last_update'),
    ]

    operations = [
        migrations.AlterField(
            model_name='placecoordinates',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2022, 12, 5, 8, 55, 38, 851207, tzinfo=utc), verbose_name='Последнее обновление'),
        ),
        migrations.AlterField(
            model_name='placecoordinates',
            name='place',
            field=models.CharField(max_length=200, unique=True, verbose_name='Место'),
        ),
        migrations.AlterField(
            model_name='placecoordinates',
            name='place_lat',
            field=models.FloatField(null=True, verbose_name='Широта'),
        ),
        migrations.AlterField(
            model_name='placecoordinates',
            name='place_lon',
            field=models.FloatField(null=True, verbose_name='Долгота'),
        ),
    ]
