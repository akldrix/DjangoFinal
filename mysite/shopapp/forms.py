from django import forms
from django.contrib.auth.models import Group
from django.core import validators

from .models import Order, Product


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "price", "description", "discount", "preview"]

    images = MultipleFileField(
        widget=MultipleFileInput(
            attrs={
                "multiple": True,
            }
        ),
        required=False,
    )


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["delivery_address", "promocode", "user", "products"]


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name"]


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
