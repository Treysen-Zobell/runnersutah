from django.contrib.auth.forms import SetPasswordForm, UserChangeForm
from django.contrib.auth.models import User


class EditPasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = [
            "new_password1",
            "new_password2",
        ]


class EditUsernameForm(UserChangeForm):
    class Meta:
        model = User
        fields = [
            "username",
        ]


class EditEmailForm(UserChangeForm):
    class Meta:
        model = User
        fields = [
            "email",
        ]
