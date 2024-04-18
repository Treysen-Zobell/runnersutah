from django import forms

from customers.models import Customer
from products.models import Product
from .models import InventoryChange


class InventoryForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "customer-select",
                "hx-get": "/inventory/load_products",
                "hx-target": "#product-select",
                "hx-indicator": ".htmx-indicator",
            }
        ),
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "product-select",
            }
        ),
    )
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
    manufacturer = forms.CharField(
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
    attachment_id = forms.FileField(required=False)

    class Meta:
        model = InventoryChange
        fields = [
            "customer",
            "product",
            "date",
            "rr",
            "po",
            "afe",
            "carrier",
            "received_transferred",
            "footage",
            "attachment_id",
            "rack_id",
            "manufacturer",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.none()

        if "customer" in self.data:
            try:
                customer_id = int(self.data["customer"])
                self.fields["product"].queryset = Product.objects.filter(
                    customer_id=customer_id
                )
            except (ValueError, TypeError):
                pass

        elif self.instance.pk:
            self.fields["product"].queryset = self.instance.customer.product_set
