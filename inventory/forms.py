from django import forms
from django.urls import reverse_lazy

from customers.models import Customer
from inventory.models import InventoryEntry
from products.models import Product


def validate_attachment_id(file):
    if not file.name.endswith(".pdf"):
        raise forms.ValidationError("Only PDFs are accepted.")


class InventoryEntryForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all().order_by("display_name"),
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "customer-select",
                "hx-get": reverse_lazy("products:load_products"),
                "hx-target": "#product-select",
                "hx-indicator": ".htmx-indicator",
            }
        ),
        required=False,
    )
    product = forms.ModelChoiceField(
        queryset=Product.objects.all().order_by("outside_diameter"),
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "id": "product-select",
            }
        ),
    )
    date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    rr = forms.CharField(required=False)
    po = forms.CharField(required=False)
    afe = forms.CharField(required=False)
    carrier = forms.CharField(required=False)
    received_transferred = forms.CharField(required=False)
    joints_in = forms.IntegerField(required=False)
    joints_out = forms.IntegerField(required=False)
    footage = forms.DecimalField()
    attachment = forms.FileField(
        required=False, widget=forms.FileInput(attrs={"accept": "application/pdf"})
    )
    manufacturer = forms.CharField(required=False)
    send_email_update = forms.ChoiceField(choices=[("yes", "Yes"), ("no", "No")])

    class Meta:
        model = InventoryEntry
        fields = (
            "product",
            "date",
            "rr",
            "po",
            "afe",
            "carrier",
            "received_transferred",
            "footage",
            "attachment",
            "manufacturer",
        )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data["joints_in"] and cleaned_data["joints_out"]:
            raise forms.ValidationError(
                "Either 'Joints In' or 'Joints Out' must be zero."
            )

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data["joints_in"]:
            instance.joints = self.cleaned_data["joints_in"]
        if self.cleaned_data["joints_out"]:
            instance.joints = -self.cleaned_data["joints_out"]
            instance.footage = -instance.footage

        if commit:
            instance.save()
        return instance
