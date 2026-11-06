from random import choices
from string import ascii_letters

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from .models import Order, Product
from .utils import add_two_numbers

User = get_user_model()


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProuctCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

        self.user = User.objects.create_user(username="testuser", password="test123")
        permission = Permission.objects.get(codename="add_product")
        self.user.user_permissions.add(permission)

    def test_create_product(self):
        self.client.login(username="testuser", password="test123")
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": "1000",
                "description": "Good table",
                "discount": "10",
            },
        )
        self.assertRedirects(response, reverse("shopapp:products"))
        self.assertTrue(Product.objects.filter(name=self.product_name).exists())


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="testuser", password="test123")
        cls.product = Product.objects.create(name="Best product", created_by=cls.user)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.product.delete()
        cls.user.delete()
        super().tearDownClass()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        "group-fixtures.json",
        "user-fixtures.json",
        "products-fixtures.json",
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products"))
        products = Product.objects.filter(archived=False).all()
        products_ = response.context["products"]

        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, "shopapp/products.html")


class OrderListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.credentials = dict(username="testuser", password="test123")
        cls.user = User.objects.create_user(**cls.credentials)
        permission = Permission.objects.get(codename="view_order")
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)

    def test_order_list_view(self):
        response = self.client.get(reverse("shopapp:order_list"))
        self.assertContains(response, "Orders:")

    def test_order_list_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:order_list"))
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        "group-fixtures.json",
        "user-fixtures.json",
        "products-fixtures.json",
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:products-export"))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data,
        )


class OrderDetailViewTestCase(TestCase):
    fixtures = [
        "group-fixtures.json",
        "user-fixtures.json",
        "products-fixtures.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.credentials = dict(username="testuser", password="test123")
        cls.user = User.objects.create_user(**cls.credentials)
        permission = Permission.objects.get(codename="view_order")
        cls.user.user_permissions.add(permission)

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)
        self.product = Product.objects.get(name="Another user product")

        self.order = Order.objects.create(
            delivery_address="Main St.",
            promocode="123",
            user=self.user,
        )
        self.order.products.add(self.product)

    def tearDown(self):
        self.order.delete()
        super().tearDown()

    def test_order_details(self):
        response = self.client.get(
            reverse("shopapp:order_detail", kwargs={"pk": self.order.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Main St.")
        self.assertContains(response, "123")
        context_order = response.context.get("order")
        self.assertIsNotNone(context_order)
        self.assertEqual(context_order.pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = [
        "group-fixtures.json",
        "user-fixtures.json",
        "products-fixtures.json",
        "order-fixtures.json",
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username="testuser", password="test123", is_staff=True
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_orders_export(self):
        response = self.client.get(reverse("shopapp:orders-export"))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user.pk,
                "products": [p.pk for p in order.products.all()],
            }
            for order in orders
        ]
        order_data = response.json()
        self.assertEqual(
            order_data["orders"],
            expected_data,
        )
