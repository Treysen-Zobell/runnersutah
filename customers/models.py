import uuid

from django.db import models
from django.contrib.auth.models import User


class Customer(User):
    display_name = models.CharField(max_length=150)
    phone_nr = models.CharField(max_length=15)

    # automated
    status = models.TextField()

    def __str__(self):
        return self.display_name
