from django import forms

from customers.models import Customer
from products.models import Product


class ProductForm(forms.ModelForm):
    CHOICES = [
        ("poly_pipe", "Poly Pipe"),
        ("line_pipe", "Line Pipe"),
        ("composite_pipe", "Composite Pipe"),
        ("flex_pipe", "Flexpipe"),
        ("tubing_sand_screens", "Tubing - Sand Screens"),
        ("tubing", "Tubing"),
        ("casing", "Casing"),
        ("other", "Other"),
    ]
    product_type = forms.ChoiceField(choices=CHOICES)
    outside_diameter_text = forms.CharField(max_length=250, required=False)
    weight_text = forms.CharField(max_length=250, required=False)
    grade = forms.CharField(max_length=250, required=False)
    coupling = forms.CharField(max_length=250, required=False)
    range = forms.CharField(max_length=250, required=False)
    condition = forms.CharField(max_length=250, required=False)
    remarks = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )
    foreman = forms.CharField(max_length=250, required=False)
    rack = forms.CharField(max_length=250)
    customer = forms.ModelChoiceField(
        label="Customer", queryset=Customer.objects.all().order_by("display_name")
    )

    class Meta:
        model = Product
        fields = (
            "product_type",
            "outside_diameter_text",
            "weight_text",
            "grade",
            "coupling",
            "range",
            "condition",
            "remarks",
            "foreman",
            "rack",
            "customer",
        )
