from django.db import models
from django.utils import timezone

class PlaceCoordinates(models.Model):

    place = models.CharField(max_length=200, unique=True)

    place_lon = models.FloatField(null=True)

    place_lat = models.FloatField(null=True)

    last_update = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return self.place
