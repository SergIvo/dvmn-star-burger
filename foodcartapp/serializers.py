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
        fields = '__all__'

    def create(self, validated_data):
        order_data = validated_data
        order_data.pop('products', None)
        return Order.objects.create(**order_data)
