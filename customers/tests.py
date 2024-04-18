from django.test import TestCase

from .models import Customer


class CustomerTestCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            username="testuser",
            password="testpassword",
            email="test@example.com",
            phone_number="+00000000000",
            display_name="Test User",
            status="Inactive",
        )
        customer.save()

    def test_customer_fields(self):
        customer = Customer.objects.get(username="testuser")

        self.assertEqual(customer.username, "testuser")
        self.assertNotEqual(customer.password, "testpassword")
        self.assertEqual(customer.email, "test@example.com")
        self.assertEqual(customer.phone_number, "+00000000000")
        self.assertEqual(customer.display_name, "Test User")
        self.assertEqual(customer.status, "Inactive")

        customer.username = "testuser2"
        customer.password = "testpassword2"
        customer.email = "test2@example.com"
        customer.phone_number = "+00000000001"
        customer.display_name = "Test User2"
        customer.status = "Active"

        self.assertEqual(customer.username, "testuser2")
        self.assertNotEqual(customer.password, "testpassword2")
        self.assertEqual(customer.email, "test2@example.com")
        self.assertEqual(customer.phone_number, "+00000000001")
        self.assertEqual(customer.display_name, "Test User2")
        self.assertEqual(customer.status, "Active")
