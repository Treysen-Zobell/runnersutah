from django.db import models

from customers.models import Customer


# Create your models here.
class Product(models.Model):
    product_type = models.CharField(max_length=250, blank=True)
    outside_diameter_text = models.CharField(max_length=250, blank=True)
    outside_diameter = models.FloatField(null=True)
    weight_text = models.CharField(max_length=250, blank=True)
    weight = models.FloatField(null=True)
    grade = models.CharField(max_length=250, blank=True)
    coupling = models.CharField(max_length=250, blank=True)
    range = models.CharField(max_length=250, blank=True)
    condition = models.CharField(max_length=250, blank=True)
    remarks = models.CharField(max_length=1000, blank=True)
    foreman = models.CharField(max_length=250, blank=True)
    rack = models.CharField(max_length=250)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    def __str__(self):
        elements = [
            self.rack,
            self.product_type,
            self.outside_diameter_text,
            self.weight_text,
            self.grade,
            self.coupling,
            self.range,
            self.condition,
        ]
        elements = [e for e in elements if e]
        return ", ".join(elements)
