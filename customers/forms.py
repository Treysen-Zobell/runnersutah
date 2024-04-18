from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    SetPasswordForm,
)

from customers.models import Customer


class RegisterForm(UserCreationForm):
    class Meta:
        model = Customer
        fields = [
            "display_name",
            "username",
            "password1",
            "password2",
            "email",
            "phone_number",
        ]


class EditForm(UserChangeForm):
    class Meta:
        model = Customer
        fields = [
            "display_name",
            "username",
            "email",
            "phone_number",
        ]


class EditPasswordForm(SetPasswordForm):
    class Meta:
        model = Customer
        fields = [
            "new_password1",
            "new_password2",
        ]


class EditUsernameForm(UserChangeForm):
    class Meta:
        model = Customer
        fields = [
            "username",
        ]


class EditEmailForm(UserChangeForm):
    class Meta:
        model = Customer
        fields = [
            "email",
        ]
