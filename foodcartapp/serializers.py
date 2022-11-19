from rest_framework.serializers import ModelSerializer
from django.core.exceptions import ValidationError

from foodcartapp.models import Order, OrderElement


class OrderElementsSerializer(ModelSerializer):
    class Meta:
        model = OrderElement
        fields = ['product', 'quantity']

    
    def validate_quantity(self, value):
        if value < 1:
            raise ValidationError('quantity cannot be less then 1')
        return value


class OrderSerializer(ModelSerializer):
    products = OrderElementsSerializer(many=True)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']

    
    def validate_products(self, value):
        if not value:
            raise ValidationError('products is empty')
        return value