# Generated by Django 3.2.15 on 2022-12-05 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0014_auto_20221205_0855'),
    ]

    operations = [
        migrations.RenameField(
            model_name='placecoordinates',
            old_name='place',
            new_name='place_name',
        ),
        migrations.AlterField(
            model_name='placecoordinates',
            name='last_update',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Последнее обновление'),
        ),
    ]
