from django.contrib.auth import get_user_model
from django.db import models

from utils.measure import convert_measure_to_mm

User = get_user_model()


class ProductTemplate(models.Model):
    """
    Represents a template for a product. Used to make a general form for creating products of a shared type.

    Reverse lookups:
        - fields: ProductTemplateField instances associated with this template.
        - notification_groups: NotificationGroup instances associated with this template.
    """

    DISCRETE = "discrete"
    CONTINUOUS = "continuous"

    COUNTING_TYPES = [
        (DISCRETE, "Discrete"),
        (CONTINUOUS, "Continuous"),
    ]

    name = models.TextField()
    format_string = models.TextField(
        help_text="Text representation of product, ex: {{title}} - {{diameter}}"
    )
    counting_type = models.TextField(choices=COUNTING_TYPES)

    def __str__(self):
        return self.name


class ProductTemplateField(models.Model):
    """
    Represents a field associated with a product template.
    """

    TEXT = "text"
    INT = "int"
    DECIMAL = "decimal"
    CHOICES = "choices"
    MEASURE = "measure"
    STATIC = "static"

    FIELD_TYPES = [
        (TEXT, "Text"),
        (INT, "Integer"),
        (DECIMAL, "Decimal"),
        (CHOICES, "Choices"),
        (MEASURE, "Measure"),
        (STATIC, "Static Text"),
    ]

    @staticmethod
    def choices_default():
        return []

    # General info for any field
    template = models.ForeignKey(
        ProductTemplate, on_delete=models.CASCADE, related_name="fields"
    )

    name = models.TextField()
    field_type = models.TextField(choices=FIELD_TYPES)
    required = models.BooleanField(default=False)

    # Info for static field
    static_text = models.TextField(help_text="Immutable text for labeling in tables")

    # Info for choices field
    choices = models.JSONField(default=choices_default)

    def __str__(self):
        return f"{self.template.name}_{self.name}"


class Product(models.Model):
    """
    Represents a specific product, which is an instance of a product template.

    Reverse lookups:
     - values: ProductFieldValue instances associated with this product
    """

    template = models.ForeignKey(ProductTemplate, on_delete=models.PROTECT)
    customers = models.ManyToManyField(
        "customers.Customer",
        related_name="products",
        blank=True,
        help_text="Customers who have this product in their stock",
    )

    def __str__(self):
        return f"{self.template.name}"


class ProductFieldValue(models.Model):
    """
    Represents the value associated with a field on a product.
    """

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="values"
    )
    field = models.ForeignKey(ProductTemplateField, on_delete=models.CASCADE)

    # Public field for each type
    value_text = models.TextField(blank=True, null=True)
    value_int = models.IntegerField(blank=True, null=True)
    value_decimal = models.DecimalField(
        blank=True, null=True, max_digits=15, decimal_places=4
    )
    value_choice = models.TextField(blank=True, null=True)
    value_measure = models.TextField(blank=True, null=True)
    value_file = models.FileField(blank=True, null=True, upload_to="../media/")

    # Hidden fields (for sorting and similar additional functionality)
    value_measure_mm = models.IntegerField(blank=True, null=True)

    class Meta:
        # Enforce only one value for each field.
        constraints = [
            models.UniqueConstraint(
                fields=["product", "field"],
                name="unique_product_field",
            )
        ]

    def __str__(self):
        return f"{self.product}.{self.field.name}"

    def save(self, *args, **kwargs):
        if self.field.field_type == ProductTemplateField.MEASURE and self.value_measure:
            self.value_measure_mm = convert_measure_to_mm(self.value_measure)
        super().save(*args, **kwargs)

    @property
    def value(self):
        return {
            "text": self.value_text,
            "int": self.value_int,
            "decimal": self.value_decimal,
            "choices": self.value_choice,
            "measure": self.value_measure,
            "static": self.field.static_text,
        }[self.field.field_type]
