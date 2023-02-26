from django.contrib import admin
from django.shortcuts import reverse, redirect
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

from foodcartapp.geocoding import fetch_coordinates
from .models import Product
from .models import ProductCategory
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order
from .models import OrderComponent


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]

    def save_model(self, request, obj, form, change):
        if obj.address and (not obj.latitude or not obj.longitude):
            try:
                latitude, longitude = fetch_coordinates(
                    settings.YANDEX_GEO_API_KEY, obj.address
                )
                obj.latitude = latitude
                obj.longitude = longitude
            except TypeError:
                pass
        super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html(
            '<img src="{url}" style="max-height: 200px;"/>', 
            url=obj.image.url
        )
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html(
            '<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>', 
            edit_url=edit_url, 
            src=obj.image.url
        )
    get_image_list_preview.short_description = 'превью'


class OrderComponentInline(admin.TabularInline):
    model = OrderComponent
    readonly_fields = ['price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'phonenumber',
        'address',
    ]
    list_display = [
        'firstname',
        'lastname',
        'phonenumber',
        'address',
    ]
    readonly_fields = ['creation_dateitme']
    inlines = [
        OrderComponentInline
    ]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if not instance.price:
                instance.price = instance.product.price
            instance.save()
        formset.save_m2m()

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        order_components = obj.components.select_related('product')
        order_products = [component.product for component in order_components]
        order_menu_items = RestaurantMenuItem.objects.filter(product__in=order_products).select_related('restaurant')

        restaurants_ids = [menu_item.restaurant.id for menu_item in order_menu_items]
        restaurant_queryset = Restaurant.objects.filter(id__in=restaurants_ids)
        form.base_fields['restaurant'].queryset = restaurant_queryset
        return form

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if url_has_allowed_host_and_scheme(request.GET.get('next'), None):
            return redirect(request.GET['next'])
        else:
            return response


@admin.register(OrderComponent)
class OrderComponentAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductCategory)
class ProductAdmin(admin.ModelAdmin):
    pass
