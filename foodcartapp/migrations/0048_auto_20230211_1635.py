# Generated by Django 3.2.15 on 2023-02-11 16:35

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_auto_20230211_1516'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('CASH', 'Наличными'), ('CARD', 'Электронно'), ('NONE', 'Не указан')], db_index=True, default='NONE', max_length=4, verbose_name='способ оплаты'),
        ),
        migrations.AlterField(
            model_name='order',
            name='creation_dateitme',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='создан'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_dateitme',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='доставлен'),
        ),
    ]
