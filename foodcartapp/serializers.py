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
        components_details = order_data.pop('products')
        order = Order.objects.create(**order_data)

        for component in components_details:
            component['order'] = order.pk
            component['price'] = component['product'].price
            component['product'] = component['product'].pk
        order_components_serializer = OrderComponentSerializer(data=components_details, many=True)
        order_components_serializer.is_valid(raise_exception=True)
        order_components_serializer.save()

        return order
