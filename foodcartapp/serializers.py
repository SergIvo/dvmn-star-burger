from django.db import transaction

from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField


from .models import Order, OrderComponent


class OrderComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderComponent
        fields = ['product', 'order', 'price', 'quantity']
        
        extra_kwargs = {'order': {'required': False}, 'price': {'required': False}}


class OrderSerializer(serializers.ModelSerializer):
    products = OrderComponentSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )
    phonenumber = PhoneNumberField(region='RU')

    class Meta:
        model = Order
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        order_data = validated_data
        order_data.pop('products', None)
        return Order.objects.create(**order_data)
