from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField


from .models import Order, OrderComponent


class OrderComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderComponent
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.ListField(
        child=OrderComponentSerializer(),
        allow_empty=False,
        write_only=True
    )
    phonenumber = PhoneNumberField(region='RU')

    class Meta:
        model = Order
        fields = ['id', 'products', 'firstname', 'lastname', 'phonenumber', 'address']
