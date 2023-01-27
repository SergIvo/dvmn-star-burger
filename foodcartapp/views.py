import phonenumbers
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


from .models import Product, Order, OrderComponent


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
    order_details = request.data

    required_types = {
        'products': list,
        'firstname': str,
        'phonenumber': str,
        'address': str,
    }

    for variable, var_type in required_types.items():
        if not isinstance(order_details.get(variable), var_type):
            return Response(
                {'TypeError': f'{variable} must have type {var_type}, not {type(order_details.get(variable))}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif not order_details.get(variable):
            return Response(
                {'ValueError': f'{variable} must not be empty or null'},
                status=status.HTTP_400_BAD_REQUEST
            )

    try:
        parsed_number = phonenumbers.parse(order_details['phonenumber'], 'RU')
        if not phonenumbers.is_valid_number(parsed_number):
            return Response(
                {'ValueError': 'Phone number is not valid'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except phonenumbers.phonenumberutil.NumberParseException:
        return Response(
                {'ValueError': 'Phone number is not valid'},
                status=status.HTTP_400_BAD_REQUEST
            )

    for component in order_details['products']:
        if not isinstance(component, dict):
            return Response(
                {'TypeError': 'Product list must only contain dictionaries'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            product_value = component['product']
            quantity_value = component['quantity']
            1 / (product_value * quantity_value)
        except KeyError:
            return Response(
                {'KeyError': 'Each product dictionary must have two keys: product, quantity'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except TypeError:
            return Response(
                {'TypeError': 'Each key in product dictionary must have type <int>'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except ZeroDivisionError:
            return Response(
                {'ValueError': 'Each key in product dictionary must not be zero'},
                status=status.HTTP_400_BAD_REQUEST
            )

    order = Order.objects.create(
        customer_name=order_details['firstname'],
        customer_last_name=order_details.get('lastname'),
        customer_phonenumber=order_details['phonenumber'],
        address=order_details['address']
    )
    for component in order_details['products']:
        try:
            product = Product.objects.get(id=component['product'])
        except ObjectDoesNotExist:
            return Response(
                {'ValueError': 'Wrong product ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        OrderComponent.objects.create(
            product=product,
            order=order,
            amount=component['quantity']
        )
    return Response(
        {'status': 'order created successfully'},
        status=status.HTTP_201_CREATED
    )
