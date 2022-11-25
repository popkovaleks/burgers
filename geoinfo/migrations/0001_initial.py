# Generated by Django 3.2.15 on 2022-11-25 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PlaceCoordinates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.CharField(max_length=200, unique=True)),
                ('place_lon', models.FloatField(null=True)),
                ('place_lat', models.FloatField(null=True)),
                ('last_update', models.DateField(auto_now=True, null=True)),
            ],
        ),
    ]
