from django import forms

from .models import Customer, Product
from .fields import ListTextWidget


class ProductForm(forms.ModelForm):
    product_type = forms.CharField(required=False)
    outside_diameter = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    weight = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        required=False,
    )
    grade = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    coupling = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    range = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    condition = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    foreman = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    customer_id = forms.ModelChoiceField(
        label="Customer",
        queryset=Customer.objects.all(),
    )

    def __init__(self, *args, **kwargs):
        product_type_list = kwargs.pop("product_type_list")
        super().__init__(*args, **kwargs)

        self.fields["product_type"].widget = ListTextWidget(
            data_list=product_type_list, name="product-list"
        )

    class Meta:
        model = Product
        fields = [
            "product_type",
            "outside_diameter",
            "weight",
            "grade",
            "coupling",
            "range",
            "condition",
            "remarks",
            "foreman",
            "customer_id",
        ]
