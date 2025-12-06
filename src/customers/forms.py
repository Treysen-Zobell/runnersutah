from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms.models import (
    modelformset_factory,
    BaseModelFormSet,
)

from customers.models import NotificationGroup
from products.models import Product, ProductTemplate


class CreateCustomerForm(UserCreationForm):
    display_name = forms.CharField(max_length=250)
    phone_number = forms.CharField(max_length=250, required=False)
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = get_user_model()
        fields = [
            "display_name",
            "phone_number",
            "products",
            "email",
            "username",
            "password1",
            "password2",
        ]


class NotificationGroupForm(forms.ModelForm):
    name = forms.CharField(max_length=250, required=True)
    templates = forms.ModelMultipleChoiceField(
        queryset=ProductTemplate.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "template-option"}),
    )

    class Meta:
        model = NotificationGroup
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["templates"].initial = [
                template.name for template in self.instance.templates.all()
            ]


NotificationGroupFormSet = modelformset_factory(
    NotificationGroup,
    form=NotificationGroupForm,
    formset=BaseModelFormSet,
    extra=0,
    can_delete=True,
)
