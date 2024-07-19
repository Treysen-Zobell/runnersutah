from django.db import models
from django.db.models import Sum, Q
from django.dispatch import receiver
from django.db.models.signals import post_save

from products.models import Product


# Create your models here.
class InventoryEntry(models.Model):
    date = models.DateField()
    rr = models.CharField(max_length=250, blank=True)
    po = models.CharField(max_length=250, blank=True)
    afe = models.CharField(max_length=250, blank=True)
    carrier = models.CharField(max_length=250, blank=True)
    received_transferred = models.CharField(max_length=250, blank=True)
    joints = models.IntegerField()
    footage = models.DecimalField(decimal_places=4, max_digits=44)
    attachment = models.FileField(upload_to="media/")
    manufacturer = models.CharField(max_length=250, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        if self.joints >= 0:
            return f"Import {self.footage}ft of {str(self.product)} in {self.joints} joints"
        else:
            return f"Export {-self.footage}ft of {str(self.product)} in {-self.joints} joints"


@receiver(post_save, sender=InventoryEntry)
def update_customer_status(sender, instance, **kwargs):
    queryset = (
        InventoryEntry.objects.filter(product__customer_id=instance.product.customer.id)
        .values("product_id", *[f"product__{n.name}" for n in Product._meta.fields])
        .annotate(total_joints=Sum("joints"), total_footage=Sum("footage"))
    )
    if queryset.filter(Q(total_joints__lt=0) | Q(total_footage__lt=0)):
        instance.product.customer.status = "Invalid"
    elif queryset.filter(Q(total_joints__gt=0) & Q(total_footage__gt=0)):
        instance.product.customer.status = "Active"
    else:
        instance.product.customer.status = "Inactive"
    instance.product.customer.save()
