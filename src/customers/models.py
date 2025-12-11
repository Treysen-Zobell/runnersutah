from django.contrib.auth import get_user_model
from django.db import models

from products.models import Product

User = get_user_model()


class Customer(models.Model):
    """
    Represents a customer with an associated user account.

    Reverse lookups:
     - notification_groups: NotificationGroup instances with this user
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(blank=False, null=False, max_length=255)
    phone_number = models.CharField(blank=True, max_length=255)
    status = models.CharField(blank=False, default="Active", max_length=255)
    products = models.ManyToManyField("products.Product", blank=True)

    def __str__(self) -> str:
        return f"{self.user} ({self.phone_number}) {self.status}"


class NotificationGroup(models.Model):
    """
    Represents a collection of email addresses with shared notification preferences, assigned to a customer.

    Reverse lookups:
     - emails: Email addresses associated with this group.
    """

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="notification_groups"
    )
    name = models.CharField(blank=False, null=False, max_length=255)
    templates = models.ManyToManyField(
        "products.ProductTemplate",
        blank=True,
        related_name="notification_groups",
        help_text="Product templates this group wants to be notified for.",
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.customer.display_name})"


class Email(models.Model):
    """
    Represents an email address that must be unique within a notification group.
    """

    group = models.ForeignKey(
        NotificationGroup, on_delete=models.CASCADE, related_name="emails"
    )
    address = models.EmailField()

    class Meta:
        # Enforce only one instance of an email address in a group
        constraints = [
            models.UniqueConstraint(
                fields=["group", "address"], name="unique_email_address"
            )
        ]

    def __str__(self) -> str:
        return self.address
