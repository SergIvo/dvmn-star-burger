from django.db import models
from django.db.models import Prefetch

from .order_model_choices import FINISH


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class OrderQuerySet(models.QuerySet):
    def with_prices(self):
        orders_with_prices = self.annotate(
            total_price=models.Sum(
                models.F('components__price') * models.F('components__quantity')
            )
        )
        return orders_with_prices
    
    def get_active_orders(self):
        products_prefetch = Prefetch('components__product')
        active_orders = (
            self.exclude(status=FINISH)
            .prefetch_related(products_prefetch)
            .select_related('restaurant').with_prices()
            .order_by('status')
        )
        return active_orders
