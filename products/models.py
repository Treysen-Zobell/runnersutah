import uuid

from django.db import models

from customers.models import Customer


class Product(models.Model):
    outside_diameter = models.FloatField(blank=True)
    weight = models.FloatField(blank=True)
    grade = models.TextField(blank=True)
    coupling = models.TextField(blank=True)
    range = models.TextField(blank=True)
    manufacturer = models.TextField(blank=True)
    condition = models.TextField(blank=True)
    condition_notes = models.TextField(blank=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.RESTRICT)

    # automated
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    def __str__(self):
        return f"OD: {self.outside_diameter}\", LBS per FT: {self.weight}#, GRADE: {self.grade}"
