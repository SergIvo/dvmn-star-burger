from typing import Tuple

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from mappoint.models import MapPoint
from mappoint.geocoding import fetch_coordinates, get_distance


def get_or_create_map_point(address) -> Tuple[float, float]:
    try:
        map_point = MapPoint.objects.get(address=address)
        address_geocode = map_point.latitude, map_point.longitude 
    except ObjectDoesNotExist:
        address_geocode = fetch_coordinates(settings.YANDEX_GEO_API_KEY, address)
        if not address_geocode:
            address_geocode = None, None
        latitude, longitude = address_geocode
        
        MapPoint.objects.create(
            address=address,
            latitude=latitude,
            longitude=longitude,
        )
    return address_geocode


def find_restaurants(order, menu_items):
    products = [component.product for component in order.components.all()]
    restaurants_with_products = {
        menu_item.restaurant for menu_item in menu_items if menu_item.product in products
    }
    return restaurants_with_products


def sort_by_distances(order, restaurants):
    order_geocode = get_or_create_map_point(order.address)
    
    restaurants_with_distances = []
    restaurants_with_no_distances = []
    for restaurant in restaurants:
        restaurant_geocode = get_or_create_map_point(restaurant.address)
        if any(restaurant_geocode) and any(order_geocode):
            restaurant.distance = get_distance(order_geocode, restaurant_geocode)
            restaurants_with_distances.append(restaurant)
        else:
            restaurant.distance = None
            restaurants_with_no_distances.append(restaurant)
    return (
        sorted(restaurants_with_distances, key=lambda x: x.distance)
        + restaurants_with_no_distances
    )
