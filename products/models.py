from django.db import models

from customers.models import Customer


class Product(models.Model):
    outside_diameter = models.TextField(blank=True)
    outside_diameter_inches = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    grade = models.TextField(blank=True)
    coupling = models.TextField(blank=True)
    range = models.TextField(blank=True)
    condition = models.TextField(blank=True)
    remarks = models.TextField(blank=True)
    foreman = models.TextField(blank=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.RESTRICT)

    def __str__(self):
        return f"OD: {self.outside_diameter} LBS/FT: {self.weight} GRADE: {self.grade}"
