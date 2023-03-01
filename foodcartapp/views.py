from django.http import JsonResponse
from django.db import transaction
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from phonenumber_field.serializerfields import PhoneNumberField


from .models import Product, Order, OrderComponent
from .serializers import OrderComponentSerializer, OrderSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        order = Order.objects.create(
            firstname=serializer.validated_data['firstname'],
            lastname=serializer.validated_data.get('lastname'),
            phonenumber=serializer.validated_data['phonenumber'],
            address=serializer.validated_data['address']
        )

        components_details = serializer.validated_data['products']
        order_components = [OrderComponent(order=order, **fields) for fields in components_details]
        for component in order_components:
            product = Product.objects.get(id=component.product_id)
            component.price = product.price
        OrderComponent.objects.bulk_create(order_components)

    new_order_serializer = OrderSerializer(order)
    return Response(
        new_order_serializer.data,
        status=status.HTTP_201_CREATED
    )
