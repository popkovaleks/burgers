from django.contrib import admin
from geoinfo.models import PlaceCoordinates


@admin.register(PlaceCoordinates)
class PlaceCoordinatesAdmin(admin.ModelAdmin):
    pass