from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.utils import timezone
from functools import reduce
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem, OrderElement
from geoinfo.geocoder import fetch_coordinates
from geoinfo.models import PlaceCoordinates


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def get_coords(place):
    place_coord, created = PlaceCoordinates.objects.get_or_create(place_name=place)
    if created or timezone.now() - place_coord.last_update > timezone.timedelta(days=30):
        try:
            address_lon, address_lat = fetch_coordinates(place)
            place_coord.place_lat = address_lat
            place_coord.place_lon = address_lon
            place_coord.last_update = timezone.now()
            place_coord.save()
            
        except TypeError as e:
            print(f'{place_coord.place_name} {e}')
    return place_coord.place_lat, place_coord.place_lon
    

@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.orders_with_cost().order_by('-status')

    for order in orders:
        if not order.cooking_restaurant:
            order_elements = order.order_elements.values_list('product', flat=True)
            restauraunts_before_intersection = []
            for element in order_elements:
                restaurants = set(RestaurantMenuItem.objects.filter(product=element).values_list('restaurant__name', flat=True))
                restauraunts_before_intersection.append(restaurants)
            shared_restaurants = reduce(lambda q1, q2: set(q1) & set(q2), restauraunts_before_intersection) if restauraunts_before_intersection else []
            
            try:
                address_lat, address_lon = get_coords(order.address)
                
                shared_restaurants_with_distance = []

                for rest in shared_restaurants:
                    rest_lat, rest_lon = get_coords(rest)
                    
                    rest_address_distance = distance.distance((rest_lat, rest_lon), (address_lat, address_lon)).km
                    shared_restaurants_with_distance.append((rest, rest_address_distance))

                    order.possible_restaurant = sorted(shared_restaurants_with_distance, key=lambda rest: rest[1])
            except TypeError:
                order.possible_restaurant = list(shared_restaurants)
    return render(request, template_name='order_items.html', context={
        'order_items': orders,
        'current_url': request.path,
    })