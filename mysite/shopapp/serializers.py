from rest_framework import serializers

from .models import Order, Product


class ProductSerializser(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "pk",
            "name",
            "description",
            "price",
            "discount",
            "created_at",
            "archived",
            "preview",
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "delivery_address",
            "promocode",
            "created_at",
            "user",
            "products",
            "receipt",
        )
