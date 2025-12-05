from decimal import Decimal

from django.db import models
from django.db.models.fields.related import ForeignKey

from utils.measure import convert_measure_to_mm


class BaseTemplateField(models.Model):
    """
    Abstract base class for template-style fields.
    """

    TEXT = "text"
    INT = "int"
    DECIMAL = "decimal"
    CHOICES = "choices"
    MEASURE = "measure"
    STATIC = "static"
    FILE = "file"

    FIELD_TYPES = [
        (TEXT, "Text"),
        (INT, "Integer"),
        (DECIMAL, "Decimal"),
        (CHOICES, "Choices"),
        (MEASURE, "Measure"),
        (STATIC, "Static Text"),
        (FILE, "File"),
    ]

    name = models.TextField()
    field_type = models.TextField(choices=FIELD_TYPES)
    required = models.BooleanField(default=False)

    static_text = models.TextField(
        blank=True, null=True, help_text="Immutable text for labeling in tables"
    )
    choices = models.JSONField(blank=True, null=True)

    class Meta:
        abstract = True

    # Must be set by subclass
    template = None

    def __str__(self) -> str:
        return f"{self.template.name}_{self.name}"


class BaseFieldValue(models.Model):
    """
    Abstract class for field-value pairs.
    """

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
        abstract = True

    # Must be set by subclass
    field = None

    def get_owner(self) -> ForeignKey:
        """
        Returns the owner of the field.

        :raises NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def __str__(self) -> str:
        return f"{self.get_owner()}.{self.field.name}"

    def save(self, *args, **kwargs) -> None:
        if self.field.field_type == BaseTemplateField.MEASURE and self.value_measure:
            self.value_measure_mm = convert_measure_to_mm(self.value_measure)
        super().save(*args, **kwargs)

    @property
    def value(self) -> str | int | Decimal:
        """
        Returns the value of the field.
        """
        return {
            "text": self.value_text,
            "int": self.value_int,
            "decimal": self.value_decimal,
            "choices": self.value_choice,
            "measure": self.value_measure,
            "static": self.field.static_text,
            "file": self.value_file.url,
        }[self.field.field_type]
