from django.contrib.auth.models import User, Group
from django.db import models


# Create your models here.
class Customer(models.Model):
    display_name = models.CharField(max_length=250)
    phone_number = models.CharField(max_length=250, blank=True)
    status = models.CharField(max_length=20, default="Active")
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.display_name


class Email(models.Model):
    address = models.TextField()
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="emails"
    )


class Tag(models.Model):
    name = models.TextField()
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name="tags")
