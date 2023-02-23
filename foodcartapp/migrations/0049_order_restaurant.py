# Generated by Django 3.2.15 on 2023-02-13 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20230211_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_orders', to='foodcartapp.restaurant', verbose_name='исполняющий ресторан'),
        ),
    ]
