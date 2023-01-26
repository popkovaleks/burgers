import requests

from star_burger.settings import GEO_CODER_API_KEY
from geoinfo.models import PlaceCoordinates

def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": GEO_CODER_API_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_or_create_place(address):
    try:
        place = PlaceCoordinates.objects.get(place_name=address)
        return place.place_lon, place.place_lat
    except PlaceCoordinates.DoesNotExist:
        place_lon, place_lat = fetch_coordinates(address)
        place = PlaceCoordinates.objects.create(
            place_name=address,
            place_lon=place_lon,
            place_lat=place_lat
        )
        return place.place_lon, place.place_lat
