from django.db import models
from django.utils import timezone

class PlaceCoordinates(models.Model):
    place_name = models.CharField(max_length=200,
        unique=True,
        verbose_name='Адрес')
    place_lon = models.FloatField(
        null=True,
        verbose_name='Долгота')
    place_lat = models.FloatField(
        null=True,
        verbose_name='Широта')
    last_update = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Последнее обновление')

    def __str__(self):
        return self.place_name
