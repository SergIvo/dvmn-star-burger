from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField

from .querysets import ProductQuerySet, OrderQuerySet
from .choices import (
    ORDER_STATUS_CHOICES, 
    CONFIRMATION, 
    PAYMENT_METHOD_CHOICES, 
    NOT_SET
)

class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class Order(models.Model):
    firstname = models.CharField(
        'имя покупателя',
        max_length=50
    )
    lastname = models.CharField(
        'фамилия покупателя',
        max_length=50,
        default='',
        blank=True
    )
    phonenumber = PhoneNumberField(
        'номер телефона покупателя',
        region='RU'
    )
    address = models.CharField(
        'адрес доставки',
        max_length=200
    )
    status = models.IntegerField(
        choices=ORDER_STATUS_CHOICES,
        default=CONFIRMATION,
        db_index=True
    )
    comment = models.TextField(
        'комментарий',
        max_length=200,
        blank=True,
    )
    creation_datetime = models.DateTimeField(
        'дата и время создания',
        default=timezone.now,
        db_index=True
    )
    confirmation_datetime = models.DateTimeField(
        'дата и время подтверждения',
        blank=True,
        null=True,
        db_index=True
    )
    delivery_datetime = models.DateTimeField(
        'дата и время доставки',
        blank=True,
        null=True,
        db_index=True
    )
    payment_method = models.CharField(
        'способ оплаты',
        max_length=4,
        choices=PAYMENT_METHOD_CHOICES,
        default=NOT_SET,
        db_index=True
    )
    restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='исполняющий ресторан',
        related_name='assigned_orders',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ на доставку'
        verbose_name_plural = 'заказы на доставку'

    def __str__(self):
        return f'{self.firstname} {self.lastname}, {self.phonenumber}'


class OrderComponent(models.Model):
    product = models.ForeignKey(
        Product,
        verbose_name='продукт',
        related_name='in_orders',
        on_delete=models.CASCADE,
    )
    order = models.ForeignKey(
        Order,
        verbose_name='заказ',
        related_name='components',
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        'стоимость',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveSmallIntegerField(
        'количество',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'компонент заказа'
        verbose_name_plural = 'компоненты заказа'

    def __str__(self):
        return f'{self.product.name}: {self.quantity}'
