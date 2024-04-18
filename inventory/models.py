from django.db import models

from customers.models import Customer
from products.models import Product


class InventoryChange(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField()
    rr = models.TextField(blank=True)
    po = models.TextField(blank=True)
    afe = models.TextField(blank=True)
    carrier = models.TextField(blank=True)
    received_transferred = models.TextField(blank=True)
    joints = models.IntegerField()
    footage = models.FloatField()
    attachment_id = models.TextField(blank=True)
    rack_id = models.TextField(blank=True)
    manufacturer = models.TextField(blank=True)

    def __str__(self):
        if self.joints >= 0:
            return f"Import {self.footage}ft of {self.product.outside_diameter} in {self.joints} joints"
        else:
            return f"Export {-self.footage}ft of {self.product.outside_diameter} in {-self.joints} joints"


class InventoryCurrent(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    last_updated = models.DateField()
    joints = models.IntegerField()
    footage = models.FloatField()
    rack_id = models.TextField(blank=True)

    def __str__(self):
        return f"{self.footage}ft of {self.product.outside_diameter} on rack {self.rack_id}"
