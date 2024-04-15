from django import forms

from customers.models import Customer
from products.models import Product
from .models import ManifestUpdate


class InventoryForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    rr = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    po = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    afe = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    carrier = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    received_transferred = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    rack_id = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    joints_in = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        required=False,
    )
    joints_out = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        required=False,
    )
    footage = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        required=False,
    )
    attachment = forms.FileField(required=False)

    class Meta:
        model = ManifestUpdate
        fields = [
            "customer_id",
            "product_id",
            "footage",
        ]
