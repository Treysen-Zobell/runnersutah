from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import models


class Customer(User):
    display_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15)
    status = models.TextField()

    def __str__(self):
        return self.display_name

    def __setattr__(self, key, value):
        """
        Override variable assignment to force encryption of password field.
        :param key: variable to assign
        :param value: value
        :return: None
        """
        if key == "password":
            self.__dict__[key] = make_password(value)
        else:
            self.__dict__[key] = value
