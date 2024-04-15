from django import forms

from .models import Customer, Product


class ProductForm(forms.ModelForm):
    outside_diameter = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    weight = forms.FloatField(
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    grade = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    coupling = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    range = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    manufacturer = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    condition = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    # condition_notes = forms.CharField(
    #     widget=forms.TextInput(attrs={"class": "form-control"}),
    # )
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
            "manufacturer",
            "condition",
            "condition_notes",
            "customer_id",
        ]
