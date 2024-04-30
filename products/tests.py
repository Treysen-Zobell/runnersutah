from django.contrib.auth.models import User
from django.test import TestCase

from .models import Customer, Product


class ProductTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="test@example.com",
        )
        customer = Customer.objects.create(
            user=user,
            phone_number="+00000000000",
            display_name="Test User",
            status="Inactive",
        )
        user2 = User.objects.create_user(
            username="testuser2",
            password="testpassword2",
            email="test2@example.com",
        )
        Customer.objects.create(
            user=user2,
            phone_number="+00000000001",
            display_name="Test User 2",
            status="Active",
        )
        Product.objects.create(
            outside_diameter='Casing 5 1/2"',
            weight=20,
            grade="J-55",
            coupling="STC",
            range="R-3",
            condition="New",
            remarks="20' Marker Joints",
            foreman="J Smith",
            customer_id=customer,
        )

    def test_product_fields(self):
        customer = Customer.objects.get(user__username="testuser")
        customer2 = Customer.objects.get(user__username="testuser2")
        product = Product.objects.get(outside_diameter='Casing 5 1/2"')

        self.assertEqual(product.outside_diameter, 'Casing 5 1/2"')
        self.assertEqual(product.weight, 20)
        self.assertEqual(product.grade, "J-55")
        self.assertEqual(product.coupling, "STC")
        self.assertEqual(product.range, "R-3")
        self.assertEqual(product.condition, "New")
        self.assertEqual(product.remarks, "20' Marker Joints")
        self.assertEqual(product.foreman, "J Smith")
        self.assertEqual(product.customer_id, customer)

        product.outside_diameter = '2"'
        product.weight = 12
        product.grade = "P110 ICY"
        product.coupling = "TSH W625"
        product.range = "R-1"
        product.condition = "Unknown"
        product.remarks = ""
        product.foreman = ""
        product.customer_id = customer2

        self.assertEqual(product.outside_diameter, '2"')
        self.assertEqual(product.weight, 12)
        self.assertEqual(product.grade, "P110 ICY")
        self.assertEqual(product.coupling, "TSH W625")
        self.assertEqual(product.range, "R-1")
        self.assertEqual(product.condition, "Unknown")
        self.assertEqual(product.remarks, "")
        self.assertEqual(product.foreman, "")
        self.assertEqual(product.customer_id, customer2)
