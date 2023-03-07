import requests

from geopy import distance


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return None
    
    try:
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    except KeyError:
        return None

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def get_distance(firt_object_coordinates, second_object_coordinates):
    objects_distance = distance.distance(
        firt_object_coordinates, 
        second_object_coordinates
    ).km
    return round(objects_distance, 3)
