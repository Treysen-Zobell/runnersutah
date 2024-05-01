from django.contrib.auth.models import User
from django.db import models


class Customer(models.Model):
    display_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=15)
    status = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return self.display_name
