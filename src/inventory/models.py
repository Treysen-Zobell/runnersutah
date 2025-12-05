from django.core.exceptions import ValidationError
from django.db import models

from utils.model_commons import BaseTemplateField, BaseFieldValue


class StorageLocation(models.Model):
    """
    Represents a storage location for products, such as a warehouse or rack.
    """

    name = models.TextField()


class InventoryChangeTemplate(models.Model):
    """
    Represents a template for an inventory entry. Used to make a general form for editing inventory for a selection of
    product templates.

    Reverse Lookups:
     - fields: InventoryChangeTemplateField instances associated with this template.
     - product_templates: ProductTemplate instances associated with this template.
    """

    DISCRETE = "discrete"
    CONTINUOUS = "continuous"

    COUNTING_TYPES = [
        (DISCRETE, "Discrete"),
        (CONTINUOUS, "Continuous"),
    ]

    name = models.TextField()
    format_string = models.TextField(
        help_text="Text representation of an inventory change, ex: {{amount}} moved on {{date}}"
    )
    counting_type = models.TextField(choices=COUNTING_TYPES, default=DISCRETE)

    def __str__(self) -> str:
        return self.name


class InventoryChangeTemplateField(BaseTemplateField):
    """
    Represents a field associated with an inventory change template.
    """

    template = models.ForeignKey(
        InventoryChangeTemplate, on_delete=models.CASCADE, related_name="fields"
    )


class InventoryChange(models.Model):
    """
    Represents a record for a change in inventory.

    Reverse lookups:
     - values: InventoryChangeFieldValue instances associated with this record.
    """

    template = models.ForeignKey(InventoryChangeTemplate, on_delete=models.PROTECT)
    customer = models.ForeignKey("customers.Customer", on_delete=models.PROTECT)
    product = models.ForeignKey("products.Product", on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    quantity_int = models.IntegerField(blank=True, null=True)
    quantity_decimal = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=4
    )
    location = models.ForeignKey(StorageLocation, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.template.name}"

    def clean(self) -> None:
        """
        Ensures that the following conditions are met:
         - Either quantity_int has a valid value if the inventory template requires discrete values, or
           quantity decimal if it requires continuous values.

        :raises ValidationError: if any condition is not met.
        """
        counting_type = self.template.counting_type
        if counting_type == InventoryChangeTemplate.DISCRETE:
            if self.quantity_int is None:
                raise ValidationError(
                    "Discrete inventory changes require quantity_int some value."
                )
            if self.quantity_decimal is not None:
                raise ValidationError(
                    "Discrete inventory changes require quantity_decimal be null"
                )
        if counting_type == InventoryChangeTemplate.CONTINUOUS:
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


class InventoryChangeFieldValue(BaseFieldValue):
    """
    Represents the value associated with a field on an inventory change.
    """

    inventory_change = models.ForeignKey(
        InventoryChange, on_delete=models.CASCADE, related_name="values"
    )
    field = models.ForeignKey(InventoryChangeTemplateField, on_delete=models.CASCADE)

    class Meta:
        # Enforce only one value for each field.
        constraints = [
            models.UniqueConstraint(
                fields=["inventory_change", "field"],
                name="unique_inventory_change_field",
            )
        ]

    def get_owner(self):
        return self.inventory_change
