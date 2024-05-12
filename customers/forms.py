from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    SetPasswordForm,
)
from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.models import User

from customers.models import Customer


class RegisterForm(UserCreationForm):
    display_name = forms.CharField()
    phone_number = forms.CharField()
    email_list = forms.CharField()

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "password1",
            "password2",
            "email",
        ]


class EditForm(UserChangeForm):
    display_name = forms.CharField()
    phone_number = forms.CharField()

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "email",
        ]


class EditPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = [
            "new_password1",
            "new_password2",
        ]


class EditUsernameForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = [
            "username",
        ]


class EditEmailForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = [
            "email",
        ]
