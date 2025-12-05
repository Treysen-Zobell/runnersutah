from django.core.exceptions import ValidationError
from django.db import models

from utils.model_commons import BaseTemplateField, BaseFieldValue
from products.models import ProductTemplate


class StorageLocation(models.Model):
    """
    Represents a storage location for products, such as a warehouse or rack.
    """

    name = models.TextField()

    def __str__(self) -> str:
        return self.name


class InventoryChangeTemplate(models.Model):
    """
    Represents a template for an inventory entry. Used to make a general form for editing inventory for a selection of
    product templates.

    Reverse Lookups:
     - fields: InventoryChangeTemplateField instances associated with this template.
     - product_templates: ProductTemplate instances associated with this template.
    """

    name = models.TextField()
    format_string = models.TextField(
        help_text="Text representation of an inventory change, ex: {{amount}} moved on {{date}}"
    )
    product_templates = models.ManyToManyField("products.ProductTemplate", blank=True)

    def __str__(self) -> str:
        return self.name


class InventoryChangeTemplateField(BaseTemplateField):
    """
    Represents a field associated with an inventory change template.
    """

    template = models.ForeignKey(
        InventoryChangeTemplate, on_delete=models.CASCADE, related_name="fields"
    )


class InventoryTransaction(models.Model):
    """
    Represents a bulk inventory transaction involving multiple products.

    Reverse lookups:
     - lines: InventoryTransactionLine instances associated with this transaction.
    """

    customer = models.ForeignKey("customers.Customer", on_delete=models.PROTECT)
    date = models.DateTimeField()

    def __str__(self) -> str:
        return f"Transaction {self.pk} ({self.date})"


class InventoryChangeLine(models.Model):
    """
    Represents a record for a change in inventory.

    Reverse lookups:
     - values: InventoryChangeFieldValue instances associated with this record.
    """

    transaction = models.ForeignKey(
        InventoryTransaction, on_delete=models.CASCADE, related_name="lines"
    )
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    location = models.ForeignKey(StorageLocation, on_delete=models.PROTECT)
    quantity_int = models.IntegerField(blank=True, null=True)
    quantity_decimal = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=4
    )

    def clean(self) -> None:
        """
        :raises ValidationError: If the quantity change is not appropriate for the product's counting type.
        """
        counting_type = self.product.template.counting_type
        if counting_type == ProductTemplate.DISCRETE:
            if self.quantity_int is None:
                raise ValidationError(
                    "Discrete inventory changes require quantity_int some value."
                )
            if self.quantity_decimal is not None:
                raise ValidationError(
                    "Discrete inventory changes require quantity_decimal be null"
                )
        if counting_type == ProductTemplate.CONTINUOUS:
            if self.quantity_int is not None:
                raise ValidationError(
                    "Continuous inventory changes require quantity_int null."
                )
            if self.quantity_decimal is None:
                raise ValidationError(
                    "Continuous inventory changes require quantity_decimal be some value."
                )

    def save(self, *args, **kwargs) -> None:
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        qty = (
            self.quantity_int
            if self.quantity_int is not None
            else self.quantity_decimal
        )
        return f"{self.product} ({qty}) @ {self.location}"


class InventoryChangeFieldValue(BaseFieldValue):
    """
    Represents the value associated with a field on an inventory change.
    """

    line = models.ForeignKey(
        InventoryChangeLine, on_delete=models.CASCADE, related_name="values"
    )
    field = models.ForeignKey(InventoryChangeTemplateField, on_delete=models.CASCADE)

    class Meta:
        # Enforce only one value for each field.
        constraints = [
            models.UniqueConstraint(
                fields=["line", "field"],
                name="unique_inventory_change_field",
            )
        ]

    def get_owner(self):
        return self.line
