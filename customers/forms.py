from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm,
)
from django.contrib.auth import get_user_model
from django import forms
from django.forms import modelformset_factory, BaseModelFormSet

from customers.models import Customer, Email


class CreateCustomerForm(UserCreationForm):
    display_name = forms.CharField(max_length=250)
    phone_number = forms.CharField(max_length=250, required=False)

    class Meta:
        model = get_user_model()
        fields = (
            "display_name",
            "phone_number",
            "username",
            "password1",
            "password2",
            "email",
        )


class UpdateCustomerForm(forms.ModelForm):
    display_name = forms.CharField(max_length=250)
    phone_number = forms.CharField(max_length=250, required=False)
    email = forms.CharField(max_length=250, required=False)

    class Meta:
        model = Customer
        fields = (
            "display_name",
            "phone_number",
            "email",
        )


class EmailForm(forms.ModelForm):
    address = forms.CharField(max_length=500, required=True)
    tags = forms.MultipleChoiceField(
        choices=[
            ("Poly Pipe", "Poly Pipe"),
            ("Line Pipe", "Line Pipe"),
            ("Composite Pipe", "Composite Pipe"),
            ("Flexpipe", "Flexpipe"),
            ("Tubing - Sand Screens", "Tubing - Sand Screens"),
            ("Tubing", "Tubing"),
            ("Casing", "Casing"),
            ("Other", "Other"),
            ("Any", "Any"),
        ],
        widget=forms.SelectMultiple(attrs={"class": "tag-option"}),
    )

    class Meta:
        model = Email
        fields = ["address"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["tags"].initial = [tag.name for tag in self.instance.tags.all()]


EmailFormSet = modelformset_factory(
    Email, form=EmailForm, formset=BaseModelFormSet, extra=0, can_delete=True
)
