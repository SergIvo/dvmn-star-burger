# Generated by Django 3.2.15 on 2023-03-01 20:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0053_auto_20230226_0152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='confirmation_dateitme',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='дата и время подтверждения'),
        ),
        migrations.AlterField(
            model_name='order',
            name='creation_dateitme',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='дата и время создания'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_dateitme',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='дата и время доставки'),
        ),
    ]