# Generated by Django 3.2.15 on 2022-11-21 12:57

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_auto_20221119_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderelement',
            name='element_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='цена'),
        ),
        migrations.AlterField(
            model_name='orderelement',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderelement', to='foodcartapp.order', verbose_name='заказ'),
        ),
    ]