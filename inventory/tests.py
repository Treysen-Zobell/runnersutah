from datetime import datetime

from django.test import TestCase

from .models import Customer, Product, InventoryChange, InventoryCurrent


class ProductTestCase(TestCase):
    def setUp(self):
        customer = Customer.objects.create(
            username="testuser",
            password="testpassword",
            email="test@example.com",
            phone_number="+00000000000",
            display_name="Test User",
            status="Inactive",
        )
        customer2 = Customer.objects.create(
            username="testuser2",
            password="testpassword2",
            email="test2@example.com",
            phone_number="+00000000001",
            display_name="Test User 2",
            status="Active",
        )
        product = Product.objects.create(
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
        product2 = Product.objects.create(
            outside_diameter='4"',
            weight=12,
            grade="P110 ICY",
            coupling="TSH W625",
            range="R-1",
            condition="B",
            remarks="23' Marker Joints",
            foreman="",
            customer_id=customer,
        )
        product3 = Product.objects.create(
            outside_diameter="1' 4\"",
            weight=26,
            grade="P110 RY",
            coupling="DWC/C-IS Plus",
            range="R-2",
            condition="E",
            remarks="",
            foreman="",
            customer_id=customer,
        )
        product4 = Product.objects.create(
            outside_diameter="1' 4\"",
            weight=26,
            grade="P110 RY",
            coupling="DWC/C-IS Plus",
            range="R-2",
            condition="E",
            remarks="",
            foreman="",
            customer_id=customer2,
        )
        InventoryChange.objects.create(
            customer=customer,
            product=product,
            date=datetime.fromisoformat("2024-04-01"),
            rr="RR# 4466 / MR21-156",
            po="Zeco# 12422",
            afe="381363",
            carrier="Runners",
            received_transferred="Ft. Worth Pipe Services Price",
            joints=12,
            footage=1248.3,
            attachment_id="",
            rack_id="B&L 8-I2",
        )
        InventoryChange.objects.create(
            customer=customer,
            product=product,
            date=datetime.fromisoformat("2024-04-04"),
            rr="RR# 4467 / MR21-157",
            po="Zeco# 12423",
            afe="381364",
            carrier="Runners",
            received_transferred="UT 11-26-4-3",
            joints=6,
            footage=673.4,
            attachment_id="",
            rack_id="B&L 8-I2",
        )
        InventoryChange.objects.create(
            customer=customer,
            product=product,
            date=datetime.fromisoformat("2024-04-05"),
            rr="RR# 4468 / MR21-158",
            po="Zeco# 12424",
            afe="381365",
            carrier="Runners",
            received_transferred="UT 11-26-4-3",
            joints=-8,
            footage=-973.4,
            attachment_id="",
            rack_id="B&L 8-I2",
        )
        InventoryChange.objects.create(
            customer=customer,
            product=product,
            date=datetime.fromisoformat("2024-04-04"),
            rr="RR# 4467 / MR21-157",
            po="Zeco# 12423",
            afe="381364",
            carrier="Runners",
            received_transferred="UT 11-26-4-3",
            joints=-3,
            footage=254.8,
            attachment_id="",
            rack_id="B&L 3-X9",
        )
        InventoryChange.objects.create(
            customer=customer2,
            product=product2,
            date=datetime.fromisoformat("2024-04-12"),
            rr="RR# 4468 / MR21-158",
            po="Zeco# 12428",
            afe="381365",
            carrier="Savage",
            received_transferred="UT 45-26-4-5",
            joints=43,
            footage=23251.3,
            attachment_id="",
            rack_id="B&L 2-AB",
        )
        InventoryChange.objects.create(
            customer=customer2,
            product=product2,
            date=datetime.fromisoformat("2024-04-14"),
            rr="RR# 4469 / MR21-159",
            po="Zeco# 12429",
            afe="381366",
            carrier="Savage",
            received_transferred="UT 45-26-4-5",
            joints=-23,
            footage=-13251.3,
            attachment_id="",
            rack_id="B&L 2-AB",
        )
        InventoryChange.objects.create(
            customer=customer2,
            product=product2,
            date=datetime.fromisoformat("2024-04-18"),
            rr="RR# 4470 / MR21-160",
            po="Zeco# 12430",
            afe="381367",
            carrier="Savage",
            received_transferred="UT 45-26-4-5",
            joints=-20,
            footage=-10000.0,
            attachment_id="",
            rack_id="B&L 2-AB",
        )

    def test_inventory_current_totals(self):
        customer = Customer.objects.get(username="testuser")
        customer2 = Customer.objects.get(username="testuser2")
        customer_inventory = InventoryCurrent.objects.filter(customer=customer)
        customer2_inventory = InventoryCurrent.objects.filter(customer=customer2)

        self.assertAlmostEqual(
            customer_inventory.get(rack_id="B&L 8-I2").footage, 948.3
        )
        self.assertEqual(customer_inventory.get(rack_id="B&L 8-I2").joints, 10)

        self.assertAlmostEqual(
            customer_inventory.get(rack_id="B&L 3-X9").footage, 254.8
        )
        self.assertEqual(customer_inventory.get(rack_id="B&L 3-X9").joints, -3)
        self.assertEqual(
            customer_inventory.get(rack_id="B&L 8-I2").customer.status, "Invalid"
        )

        self.assertAlmostEqual(customer2_inventory.get(rack_id="B&L 2-AB").footage, 0)
        self.assertEqual(customer2_inventory.get(rack_id="B&L 2-AB").joints, 0)
        self.assertEqual(
            customer2_inventory.get(rack_id="B&L 2-AB").customer.status, "Inactive"
        )

        inventory_change = InventoryChange.objects.get(rack_id="B&L 3-X9")
        inventory_change.joints = 3
        inventory_change.save()

        self.assertEqual(
            customer_inventory.get(rack_id="B&L 8-I2").customer.status, "Active"
        )
