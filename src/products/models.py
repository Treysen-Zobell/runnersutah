from django.db import models

from utils.model_commons import BaseTemplateField, BaseFieldValue


class ProductTemplate(models.Model):
    """
    Represents a template for a product. Used to make a general form for creating products of a shared type.

    Reverse lookups:
        - fields: ProductTemplateField instances associated with this template.
        - notification_groups: NotificationGroup instances associated with this template.
    """

    name = models.TextField()
    format_string = models.TextField(
        help_text="Text representation of product, ex: {{title}} - {{diameter}}"
    )
    inventory_change_template = models.OneToOneField(
        "inventory.InventoryChangeTemplate",
        on_delete=models.PROTECT,
        related_name="product_templates",
    )

    def __str__(self) -> str:
        return self.name


class ProductTemplateField(BaseTemplateField):
    """
    Represents a field associated with a product template.
    """

    template = models.ForeignKey(
        ProductTemplate, on_delete=models.CASCADE, related_name="fields"
    )


class Product(models.Model):
    """
    Represents a specific product, which is an instance of a product template.

    Reverse lookups:
     - values: ProductFieldValue instances associated with this product.
    """

    template = models.ForeignKey(ProductTemplate, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return f"{self.template.name}"


class ProductFieldValue(BaseFieldValue):
    """
    Represents the value associated with a field on a product.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="values"
    )
    field = models.ForeignKey(ProductTemplateField, on_delete=models.CASCADE)

    class Meta:
        # Enforce only one value for each field.
        constraints = [
            models.UniqueConstraint(
                fields=["product", "field"],
                name="unique_product_field",
            )
        ]

    def get_owner(self):
        return self.product
