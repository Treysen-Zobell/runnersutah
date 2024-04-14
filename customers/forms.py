from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    UserChangeForm,
    SetPasswordForm,
)

from customers.models import Customer


class RegisterForm(UserCreationForm):
    display_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Name", "class": "form-control"}),
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        ),
    )
    password1 = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        ),
    )
    password2 = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm Password", "class": "form-control"}
        ),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"placeholder": "Email", "class": "form-control"}
        ),
    )
    phone_nr = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Phone Number", "class": "form-control"}
        ),
    )

    class Meta:
        model = Customer
        fields = [
            "display_name",
            "username",
            "password1",
            "password2",
            "email",
            "phone_nr",
        ]


class EditForm(UserChangeForm):
    display_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Name", "class": "form-control"}),
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        ),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"placeholder": "Email", "class": "form-control"}
        ),
    )
    phone_nr = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(
            attrs={"placeholder": "Phone Number", "class": "form-control"}
        ),
    )

    class Meta:
        model = Customer
        fields = [
            "display_name",
            "username",
            # "password1",
            # "password2",
            "email",
            "phone_nr",
        ]


class EditPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control",
            }
        ),
    )
    new_password2 = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = Customer
        fields = [
            "new_password1",
            "new_password2",
        ]
