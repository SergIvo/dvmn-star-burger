from django.db import models


class MapPoint(models.Model):
    address = models.CharField(
        'адрес',
        max_length=100,
        unique=True
    )
    latitude = models.FloatField(
        verbose_name='Широта',
        blank=True,
        null=True
    )
    longitude = models.FloatField(
        verbose_name='Долгота',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'место на карте'
        verbose_name_plural = 'места на карте'

    def __str__(self):
        return self.address
