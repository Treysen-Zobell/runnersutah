from datetime import datetime

from django.db import models
from django.db.models.signals import post_delete, post_save
from django.db.models import Q
from django.dispatch import receiver

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


def calculate_current_inventory(customer: Customer, product: Product, rack_id: str):
    """
    Recalculates the current inventory for the resource affected by the change.
    :return:
    """
    inventory_current = (
        InventoryCurrent.objects.filter(customer=customer)
        .filter(product=product)
        .filter(rack_id=rack_id)
    )

    if len(inventory_current) == 0:
        inventory_current = InventoryCurrent(
            customer=customer,
            product=product,
            last_updated=datetime.now(),
            joints=0,
            footage=0,
            rack_id=rack_id,
        )

    else:
        inventory_current = inventory_current[0]

    inventory_current.last_updated = datetime.now()
    inventory_current.footage = 0
    inventory_current.joints = 0
    for inv in InventoryChange.objects.filter(
        customer=customer, product=product, rack_id=rack_id
    ):
        inventory_current.joints += inv.joints
        inventory_current.footage += inv.footage
    inventory_current.save()

    # Update status on customer
    active = (
        InventoryCurrent.objects.filter(customer=customer)
        .filter(footage__gt=0)
        .filter(joints__gt=0)
        .count()
    )
    invalid = (
        InventoryCurrent.objects.filter(customer=customer).filter(footage__lt=0).count()
        + InventoryCurrent.objects.filter(customer=customer)
        .filter(joints__lt=0)
        .count()
    )

    if invalid > 0:
        customer.status = "Invalid"
    elif active > 0:
        customer.status = "Active"
    else:
        customer.status = "Inactive"
    customer.save()


@receiver(post_delete, sender=InventoryChange)
def inventory_delete(sender, instance: InventoryChange, **kwargs):
    calculate_current_inventory(instance.customer, instance.product, instance.rack_id)


@receiver(post_save, sender=InventoryChange)
def inventory_save(sender, instance: InventoryChange, **kwargs):
    calculate_current_inventory(instance.customer, instance.product, instance.rack_id)
