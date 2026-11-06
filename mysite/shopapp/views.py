"""
В этом модуле лежат различные наборы представлений.

Разные view интернет-магазина: по товарам, заказам и тд
"""

import random
from csv import DictWriter

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.db.models import QuerySet
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from shopapp.common import save_csv_products
from shopapp.forms import GroupForm, ProductForm
from shopapp.models import Order, Product, ProductImage
from shopapp.serializers import OrderSerializer, ProductSerializser


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product
    Полный CRUD для сущностей товара
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializser
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "price",
        "discount",
        "archived",
    ]
    ordering_fields = ["pk", "name", "price", "discount"]

    @extend_schema(
        summary="Get one product by id",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializser,
            404: OpenApiResponse(description="Empty response, product id not found"),
        },
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)

    @action(methods=["GET"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({field: getattr(product, field) for field in fields})

        return response

    @action(detail=False, methods=["POST"], parser_classes=[MultiPartParser])
    def upload_csv(self, request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @method_decorator(cache_page(60))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all().select_related("user").prefetch_related("products")
    serializer_class = OrderSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["delivery_address", "user"]
    filterset_fields = [
        "delivery_address",
        "user",
        "promocode",
        "products",
    ]
    ordering_fields = ["pk", "delivery_address", "user", "products"]


class ShopIndexView(View):
    # @method_decorator(cache_page(30))
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ("Laptop", 2000),
            ("Smartphone", 1000),
        ]
        rand = random.random()
        context = {
            "products": products,
            "rand": rand,
        }
        print("shop index context", context)

        return render(request, "shopapp/shop-index.html", context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related("permissions").all(),
        }
        return render(request, "shopapp/groups-list.html", context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect(request.path)


class ProductDetailView(DetailView):
    template_name = "shopapp/product-details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = "shopapp/products.html"
    queryset = Product.objects.filter(archived=False)
    context_object_name = "products"


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.select_related("user").prefetch_related("products")


class OrdersDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "shopapp.view_order"
    queryset = Order.objects.select_related("user").prefetch_related("products")


class OrderCreateView(CreateView):
    model = Order
    fields = "delivery_address", "promocode", "user", "products"
    success_url = reverse_lazy("shopapp:order_list")


class OrderUpdateView(UpdateView):
    queryset = Order.objects.select_related("user").prefetch_related("products")
    fields = "delivery_address", "promocode", "user", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:order_detail",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:order_list")


class ProductCreateView(UserPassesTestMixin, CreateView):
    def test_func(self) -> bool:
        return self.request.user.has_perm("shopapp.add_product")

    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy("shopapp:products")

    def form_valid(self, form) -> HttpResponse:
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self) -> bool:
        if self.request.user.is_superuser:
            return True
        product = self.get_object()
        return (
            self.request.user.has_perm("shopapp.change_product")
            and self.request.user == product.created_by
        )

    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    form_class = ProductForm
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                images=image,
            )
        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


class ProductExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        products_data = cache.get(cache_key)
        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": str(product.price),
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)

        return JsonResponse({"products": products_data})


class OrderExportView(UserPassesTestMixin, View):
    def test_func(self) -> bool:
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.order_by("pk").all()
        order_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user": order.user.pk,
                "products": [p.pk for p in order.products.all()],
            }
            for order in orders
        ]

        return JsonResponse({"orders": order_data})


class LatestProductsFeed(Feed):
    title = "Shop Products (latest)"
    description = "Updates on changes and addition of product list"
    link = reverse_lazy("shopapp:products")

    def items(self) -> QuerySet[Product]:
        return Product.objects.order_by("pk")[:5]

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200]


class UserOrdersListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "shopapp/user-orders.html"
    context_object_name = "orders"

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")

        return Order.objects.filter(user_id=user_id).order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_id = self.kwargs.get("user_id")

        context["target_user"] = get_object_or_404(User, pk=user_id)

        return context


class UserOrderExportView(View):
    def get(self, request: HttpRequest, user_id: int) -> JsonResponse:

        cache_key = f"user_orders_export_{user_id}"
        serialized_data = cache.get(cache_key)

        if serialized_data is None:
            user = get_object_or_404(User, pk=user_id)

            orders = (
                Order.objects.filter(user=user)
                .prefetch_related("products")
                .order_by("pk")
            )
            serializer = OrderSerializer(orders, many=True)
            serialized_data = serializer.data

            cache.set(cache_key, serialized_data, 300)

        return JsonResponse(serialized_data, safe=False)
