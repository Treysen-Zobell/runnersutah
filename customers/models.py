import uuid

from django.db import models
from django.utils import timezone


class AutoDateTimeField(models.DateTimeField):
    def pre_save(self, model_instance, add):
        return timezone.now()


class Customer(models.Model):
    username = models.TextField()
    password_hashed = models.TextField()
    display_name = models.TextField()
    email = models.EmailField(blank=True)
    phone_nr = models.TextField(blank=True)

    # automated
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_on = models.DateTimeField(default=timezone.now)
    modified_on = AutoDateTimeField(default=timezone.now)
    status = models.TextField()

    def __str__(self):
        return self.display_name
