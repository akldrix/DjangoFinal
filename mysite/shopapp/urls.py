from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    GroupsListView,
    OrderCreateView,
    OrderDeleteView,
    OrderExportView,
    OrderViewSet,
    OrdersDetailView,
    OrdersListView,
    OrderUpdateView,
    ProductCreateView,
    ProductDeleteView,
    ProductDetailView,
    ProductExportView,
    ProductsListView,
    ProductUpdateView,
    ShopIndexView,
    ProductViewSet,
)


app_name = "shopapp"
routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)


urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("api/", include(routers.urls)),
    path("products/", ProductsListView.as_view(), name="products"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product_details"),
    path(
        "products/<int:pk>/update/", ProductUpdateView.as_view(), name="product_update"
    ),
    path(
        "products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"
    ),
    path("products/export/", ProductExportView.as_view(), name="products-export"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/create", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/update/", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete/", OrderDeleteView.as_view(), name="order_delete"),
    path("orders/<int:pk>/", OrdersDetailView.as_view(), name="order_detail"),
    path("orders/export/", OrderExportView.as_view(), name="orders-export"),
]
