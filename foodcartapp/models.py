from django.db import models
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def orders_with_cost(self):
        return self\
            .annotate(cost=Sum(F('orderelement__element_price')*F('orderelement__quantity')))



class Order(models.Model):
    objects = OrderQuerySet.as_manager()

    firstname = models.CharField(
        'имя',
        max_length=200)

    lastname = models.CharField(
        'фамилия',
        max_length=200)

    phonenumber = PhoneNumberField('номер телефона')

    address = models.CharField(
        'адрес',
        max_length=200)

    CREATED = 'CR'
    COOKING = 'CK'
    DELIVERY = 'DL'
    DONE = 'DN'

    ORDER_STATUSES = [
        (CREATED, 'Created'),
        (COOKING, 'Cooking'),
        (DELIVERY, 'Delivery'),
        (DONE, 'Done')
    ]


    status = models.CharField(
        max_length=2,
        choices=ORDER_STATUSES,
        default=CREATED
    )

    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    called_at = models.DateTimeField(null=True)

    delivered_at = models.DateTimeField(null=True)


    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f"{self.firstname} - {self.address}"


class OrderElement(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='orderelement',
        verbose_name='заказ',
        on_delete=models.CASCADE)

    product = models.ForeignKey(
        Product,
        verbose_name='продукт',
        on_delete=models.CASCADE
    )

    element_price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )

    quantity = models.IntegerField(verbose_name='количество')

    def set_element_price(self):
        self.element_price = self.product.price