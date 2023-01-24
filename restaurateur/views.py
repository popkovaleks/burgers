from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.utils import timezone
from django.db.models import OuterRef, Subquery
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem, OrderElement
from geoinfo.geocoder import get_or_create_place
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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    places = PlaceCoordinates.objects.filter(place_name=OuterRef('address'))
    orders = Order.objects.orders_with_cost().order_by('-status')\
        .annotate(lon=Subquery(places.values('place_lon')), lat=Subquery(places.values('place_lat')))
    restaurants = Restaurant.objects.all().prefetch_related('menu_items')\
        .annotate(lon=Subquery(places.values('place_lon')), lat=Subquery(places.values('place_lat')))
    
    for order in orders:
        if order.cooking_restaurant:
            continue

        order_elements = set(item.product for item in order.elements.all())
        possible_restaurants = []
        for restaurant in restaurants:
            rest_products = set(element.product for element in restaurant.menu_items.all())
            if order_elements.issubset(rest_products):
                possible_restaurants.append(restaurant.name)
        
        if not (order.lon or order.lat):
            try:
                order.lon, order.lat = get_or_create_place(order.address)
            except TypeError:
                pass
            
        shared_restaurants_with_distance = []

        for rest in possible_restaurants:
            try:
                rest_lon, rest_lat = get_or_create_place(rest)
            except TypeError:
                order.possible_restaurant = list(possible_restaurants)
                continue
            
            rest_address_distance = distance.distance((rest_lat, rest_lon), (order.lat, order.lon)).km
            shared_restaurants_with_distance.append((rest, rest_address_distance))
            
            order.possible_restaurant = sorted(shared_restaurants_with_distance, key=lambda rest: rest[1])
        

    return render(request, template_name='order_items.html', context={
        'order_items': orders,
        'current_url': request.path,
    })