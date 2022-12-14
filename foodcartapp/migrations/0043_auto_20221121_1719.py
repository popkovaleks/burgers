# Generated by Django 3.2.15 on 2022-11-21 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0042_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('CR', 'Created'), ('CK', 'Cooking'), ('DL', 'Delivery'), ('DN', 'Done')], default='CR', max_length=2),
        ),
    ]
