from django.contrib.auth.models import User
from django.test import TestCase

from .models import Customer


class CustomerTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com",
        )
        Customer.objects.create(
            user=user,
            phone_number="+00000000000",
            display_name="Test User",
            status="Inactive",
        )

    def test_customer_fields(self):
        customer = Customer.objects.get(user__username="testuser")

        self.assertEqual(customer.user.username, "testuser")
        self.assertNotEqual(customer.user.password, "testpassword")
        self.assertEqual(customer.user.email, "test@example.com")
        self.assertEqual(customer.phone_number, "+00000000000")
        self.assertEqual(customer.display_name, "Test User")
        self.assertEqual(customer.status, "Inactive")

        customer.user.username = "testuser2"
        customer.user.password = "testpassword2"
        customer.user.email = "test2@example.com"
        customer.phone_number = "+00000000001"
        customer.display_name = "Test User2"
        customer.status = "Active"

        self.assertEqual(customer.user.username, "testuser2")
        self.assertNotEqual(customer.user.password, "testpassword2")
        self.assertEqual(customer.user.email, "test2@example.com")
        self.assertEqual(customer.phone_number, "+00000000001")
        self.assertEqual(customer.display_name, "Test User2")
        self.assertEqual(customer.status, "Active")
