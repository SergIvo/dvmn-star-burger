from typing import Tuple

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.db.models import Prefetch
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem
from mappoint.models import MapPoint
from mappoint.geocoding import fetch_coordinates, get_distance


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


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


def find_restaurants(order, products, menu_items):
    order_geocode = get_or_create_map_point(order.address)
    
    restaurants_with_products = {
        menu_item.restaurant for menu_item in menu_items if menu_item.product in products
    }
    restaurants_with_distances = []
    restaurants_with_no_distances = []
    for restaurant in restaurants_with_products:
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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    products_prefetch = Prefetch('components__product')
    orders = list(
        Order.objects.exclude(status=Order.FINISH)
        .prefetch_related(products_prefetch)
        .select_related('restaurant').with_prices()
        .order_by('status')
    )
    menu_items = RestaurantMenuItem.objects.filter(availability=True).select_related('restaurant', 'product')
    for order in orders:
        if not order.restaurant:
            products = [component.product for component in order.components.all()]
            order.restaurants_ready_to_cook = find_restaurants(
                order,
                products,
                menu_items
            )
    return render(request, template_name='order_items.html', context={
        'order_items': orders
    })
