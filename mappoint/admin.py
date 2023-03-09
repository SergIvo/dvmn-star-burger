from django.contrib import admin
from django.conf import settings

from mappoint.geocoding import fetch_coordinates
from .models import MapPoint


@admin.register(MapPoint)
class MapPointAdmin(admin.ModelAdmin):
    list_display = [
        'address',
        'latitude',
        'longitude',
    ]

    def save_model(self, request, obj, form, change):
        if 'address' in form.changed_data:
            print('Address changed')
            try:
                latitude, longitude = fetch_coordinates(
                    settings.YANDEX_GEO_API_KEY, obj.address
                )
                obj.latitude = latitude
                obj.longitude = longitude
            except TypeError:
                pass
        super().save_model(request, obj, form, change)
