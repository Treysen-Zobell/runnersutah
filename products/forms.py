from django import forms

from .models import Customer, Product


class ProductForm(forms.ModelForm):
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

    class Meta:
        model = Product
        fields = [
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
