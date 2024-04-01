import uuid

from django.db import models

from customers.models import Customer
from products.models import Product


class ManifestUpdate(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.RESTRICT)
    product_id = models.ForeignKey(Product, on_delete=models.RESTRICT)
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

    # automated
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    def __str__(self):
        if self.joints >= 0:
            return f"Import {self.joints} {self.product_id.outside_diameter}\" from {self.customer_id.display_name}"
        else:
            return f"Export {-self.joints} {self.product_id.outside_diameter}\" from {self.customer_id.display_name}"
