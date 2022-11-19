from django.http import JsonResponse
from django.templatetags.static import static
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from phonenumber_field.validators import validate_international_phonenumber
import json


from .models import Product, Order, OrderElement


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def validate_order_data(order_data):
    set_of_required_keys = {'products', 'firstname', 'lastname', 'phonenumber', 'address'}
    empty_keys = set_of_required_keys - set(order_data)
    if empty_keys:
        keys_in_error = ', '.join(empty_keys)
        return Response({"error":f"{keys_in_error} required"},status=status.HTTP_400_BAD_REQUEST)
    for key in order_data.keys():
        print(key)
        if key == 'products':
            if order_data.get('products') is None:
                return Response({"error":"products is required field"},status=status.HTTP_400_BAD_REQUEST)

            if not isinstance(order_data.get('products'), list):
                return Response({"error":"products is not a list"},status=status.HTTP_400_BAD_REQUEST)

            if order_data.get('products') == []:
                return Response({"error":"products is an empty list"},status=status.HTTP_400_BAD_REQUEST)

            for product in order_data['products']:
                product_in_db = get_object_or_404(Product, pk=product.get('product'))
                if not isinstance(product.get('quantity'), int):
                    return Response({"error":"quantity is not int"},status=status.HTTP_400_BAD_REQUEST)
                if product['quantity'] < 1:
                    return Response({"error":"quantity is less than 1"},status=status.HTTP_400_BAD_REQUEST)
        else:
            if not order_data.get(key):
                return Response({"Error":f"{key} is empty"},status=status.HTTP_400_BAD_REQUEST)
            
            if not isinstance(order_data[key], str):
                return Response({"error":f"{key} is not a string"},status=status.HTTP_400_BAD_REQUEST)
            
            if key == 'phonenumber':
                try:
                    validate_international_phonenumber(order_data[key])
                except ValidationError:
                    return Response({"error":"invalid phone number"},status=status.HTTP_400_BAD_REQUEST)
                    


@api_view(['POST'])
def register_order(request):
    try:
        order_data = request.data
        print(order_data)

        response = validate_order_data(order_data)
            
        # if order_data.get('firstname') is None\
        #     and order_data.get('lastname') is None\
        #     and order_data.get('phonenumber') is None\
        #     and order_data.get('address') is None:
        #     return Response({"error":"firstname, lastname, phonenumber, address cannot be empty"})




        # if order_data.get('firstname') is None:
        #     return Response({"error":"firstname cannot be empty"})
        if not response:
            order = Order.objects.create(
                name = order_data.get('firstname', ''),
                last_name = order_data.get('lastname',''),
                phone_number = order_data['phonenumber'],
                address = order_data['address']
            )

            if order:
                print(order)
                for product in order_data['products']:
                    print(product)
                    OrderElement.objects.create(
                        order=order,
                        product_id=product['product'],
                        quantity=product['quantity']
                    )
            
            response = Response({}, status=status.HTTP_200_OK)
    except ValueError as e:
        print(e)
    return response
