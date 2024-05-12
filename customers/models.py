import json
from typing import List, Dict, Optional

from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    display_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15)
    status = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.display_name


class Email(models.Model):
    address = models.TextField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Tag(models.Model):
    name = models.TextField()
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
