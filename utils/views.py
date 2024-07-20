import sqlite3
from fractions import Fraction
from io import BytesIO
from typing import List, Any
import re
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.core.files import File
from django.shortcuts import redirect
from django.urls import reverse_lazy

from faker import Faker
import random
import xlsxwriter

from customers.models import Customer, Email, Tag
from inventory.models import InventoryEntry
from products.models import Product
from products.views import convert_inches, convert_weight


# Create your views here.
@login_required
def populate_tables(request):
    # Clear out old entries
    User.objects.filter(~Q(username="admin")).delete()

    fake = Faker()
    # Generate customers
    for _ in range(20):
        username = fake.user_name()
        email = fake.email()
        password = fake.word()
        display_name = fake.first_name() + " " + fake.last_name()
        phone_number = fake.phone_number()

        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        customer = Customer.objects.create(
            user=user, display_name=display_name, phone_number=phone_number
        )

        # Generate email list
        for _ in range(random.randint(1, 4)):
            email_address = fake.email()
            email = Email.objects.create(address=email_address, customer=customer)

            # Generate tags
            for _ in range(random.randint(1, 4)):
                tag_name = random.choice(
                    ("Line Pipe", "Flex", "Tubing", "Sand Screens", "Other", "")
                )
                Tag.objects.create(name=tag_name, email=email)

        # Generate products
        for _ in range(10):
            product_type = random.choice(
                ("Line Pipe", "Flex", "Tubing", "Sand Screens", "Other", "")
            )
            outside_diameter_text = approximate_fraction(random.uniform(0.2, 12.5))
            weight_text = f"{random.randint(1, 12)}#"
            grade = random.choice(("L-80", "J-55", "HC L-80", "X52"))
            coupling = random.choice(("EUE 8rd T&C", "BTC", "GBCD", "PEB"))
            _range = f"R-{random.randint(1, 5)}"
            condition = random.choice(("A", "B", "C", "D", "F", "Scrap"))
            remarks = " ".join([fake.word() for _ in range(random.randint(1, 200))])
            foreman = fake.first_name()
            rack = (
                random.choice(("XCL", "CH4", "SCO", "Fin", "P2E"))
                + str(random.randint(1, 10))
                + "-"
                + str(random.randint(1, 30))
            )

            product = Product.objects.create(
                product_type=product_type,
                outside_diameter_text=outside_diameter_text,
                outside_diameter=convert_inches(outside_diameter_text),
                weight_text=weight_text,
                weight=convert_weight(weight_text),
                grade=grade,
                coupling=coupling,
                range=_range,
                condition=condition,
                remarks=remarks,
                foreman=foreman,
                rack=rack,
                customer=customer,
            )

            # Generate inventory records
            for _ in range(10):
                date = fake.date()
                rr = fake.word()
                po = fake.word()
                afe = fake.word()
                carrier = fake.word()
                received_transferred = fake.word()
                joints = random.randint(-50, 50)
                if joints >= 0:
                    footage = random.uniform(10.0, 500.0)
                else:
                    footage = random.uniform(-500.0, -10.0)
                manufacturer = fake.word()

                InventoryEntry.objects.create(
                    date=date,
                    rr=rr,
                    po=po,
                    afe=afe,
                    carrier=carrier,
                    received_transferred=received_transferred,
                    joints=joints,
                    footage=footage,
                    manufacturer=manufacturer,
                    product=product,
                )

    return HttpResponse("Ok")


def approximate_fraction(decimal):
    if decimal == 0:
        return Fraction(0)

    sign = 1 if decimal > 0 else -1
    decimal = abs(decimal)

    # List of denominators as powers of 2 up to 32
    denominators = [2**i for i in range(6)]  # 2^0, 2^1, ..., 2^5 (1, 2, 4, 8, 16, 32)

    closest_fraction = None
    min_difference = float("inf")

    for denom in denominators:
        fraction = Fraction(decimal).limit_denominator(denom)
        difference = abs(decimal - float(fraction))

        if difference < min_difference:
            min_difference = difference
            closest_fraction = fraction

    return str(closest_fraction * sign) + '"'


@login_required
def login_redirect(request):
    if request.user.groups.filter(name="admin").exists():
        return redirect("customers:list")
    else:
        customer = Customer.objects.filter(user_id=request.user.id).first()
        return redirect("inventory:customer_report", customer_id=customer.id)


# @login_required
# def migrate_db(request):
#     if not request.user.groups.filter(name="admin").exists():
#         return HttpResponse(status=403)
#
#     db_filename = request.GET.get("file", "old.sqlite")
#     db = sqlite3.connect(db_filename)
#     cursor = db.cursor()
#
#     print("Resetting database...")
#     User.objects.filter(~Q(username="admin")).delete()
#     print("Database cleared! Starting migrations...")
#
#     # ------------------------------------------------------
#
#     customer_dict = {}
#     product_dict = {}
#
#     # Import customers from old DB
#     old_users = cursor.execute("SELECT * FROM users").fetchall()
#     for (
#         user_id,
#         username,
#         display_name,
#         email,
#         phone,
#         _,
#         _,
#         password,
#         _,
#         _,
#         _,
#         user_role,
#         _,
#     ) in old_users:
#         if username == "admin":
#             continue
#
#         username = username.replace('\\"', '"')
#         display_name = display_name.replace('\\"', '"')
#         email = email.replace('\\"', '"')
#         phone = phone.replace('\\"', '"')
#         password = password.replace('\\"', '"')
#         username = username.replace('\\"', '"')
#
#         user = User.objects.create_user(
#             username=username,
#             password=password,
#             email=email,
#         )
#         group = Group.objects.get(name="customer")
#         group.user_set.add(user)
#
#         customer = Customer.objects.create(
#             user=user,
#             phone_number=phone,
#             display_name=display_name,
#         )
#         customer_dict[user_id] = customer
#
#     # Import products from old DB
#     old_products = cursor.execute("SELECT * FROM products").fetchall()
#     for (
#         product_id,
#         od,
#         _,
#         weight,
#         end_type,
#         grade,
#         coating,
#         foreman,
#         customer_id,
#     ) in old_products:
#         # Clean inputs
#         od = od.replace('\\"', '"')
#         diameter = []
#         product_type = []
#         for ele in od.replace('\\"', '"').split(" "):
#             if any(char.isdigit() for char in ele) or ele == "x":
#                 diameter.append(ele)
#             else:
#                 product_type.append(ele)
#         diameter = " ".join(diameter)
#         product_type = " ".join(product_type)
#
#         weight = weight.replace('\\"', '"')
#         end_type = end_type.replace('\\"', '"')
#         grade = grade.replace('\\"', '"')
#         foreman = foreman.replace('\\"', '"')
#
#         # Split grade column to extract data
#         elements = grade.split(",")
#         if len(elements) == 1:
#             elements = grade.split(" ")
#         elements = [ele.strip() for ele in elements if ele.strip() != ""]
#
#         grade = ""
#         coupling = ""
#         pipe_range = ""
#         condition = ""
#
#         for element in elements:
#             # Range
#             if re.match(r"R-?\d+", element):
#                 pipe_range = re.findall(r"R-?\d+", element)[0]
#
#             # Condition
#             elif re.match(r"(\w+)-Condition", element):
#                 condition = re.findall(r"(\w+)-Condition", element)[0]
#             elif any(i in element for i in ["New", "Unknown"]):
#                 condition = element
#
#             # Grade
#             elif any(
#                 [
#                     i in element
#                     for i in [
#                         "J-55",
#                         "L-80",
#                         "Seah",
#                         "P110",
#                         "Grade",
#                         "X52",
#                         "X42",
#                         "T95",
#                         "CP80",
#                         "Junk",
#                         "N-80",
#                         "HCP-",
#                         "DP-API",
#                         "P-110",
#                     ]
#                 ]
#             ):
#                 grade = element
#
#             # Coupling
#             elif any(
#                 [
#                     i in element
#                     for i in [
#                         "VAM",
#                         "GBCD",
#                         "BTC",
#                         "DWC/",
#                         "EUE",
#                         "GB CD",
#                         "ERW",
#                         "Vamedge",
#                         "PH6",
#                         "LTC",
#                         "TSH",
#                         "STC",
#                         "VA",
#                         "Ultra",
#                         "S135",
#                         "STL",
#                     ]
#                 ]
#             ):
#                 coupling = element
#
#         elements.append(end_type)
#         remarks = ", ".join(elements)
#
#         product = Product.objects.create(
#             product_type=product_type,
#             outside_diameter_text=diameter,
#             outside_diameter=convert_inches(od),
#             weight=convert_weight(weight),
#             weight_text=weight,
#             grade=grade,
#             coupling=coupling,
#             range=pipe_range,
#             condition=condition,
#             remarks=remarks,
#             foreman=foreman,
#             customer=customer_dict[customer_id],
#         )
#         product_dict[product_id] = product
#
#     old_inventory = cursor.execute("SELECT * FROM store").fetchall()
#     for i, (
#         inventory_id,
#         customer_id,
#         product_id,
#         c_date,
#         rr,
#         po,
#         carrier,
#         received_transferred,
#         joints_in,
#         joints_out,
#         footage,
#         attachment,
#         manufacturer,
#         rack,
#         afe,
#         added_by,
#         c_datetime,
#     ) in enumerate(old_inventory):
#         # print(f"{(i / len(old_inventory)) * 100:.2f}%")
#
#         rack_id = cursor.execute(
#             "SELECT coating FROM products WHERE product_id = ?", (product_id,)
#         ).fetchone()
#         if rack_id is None:
#             print(f"Product {product_id} does not exist")
#             rack_id = "default"
#         else:
#             rack_id = rack_id[0]
#
#         c_date = c_date.replace('\\"', '"')
#         rr = rr.replace('\\"', '"')
#         po = po.replace('\\"', '"')
#         carrier = carrier.replace('\\"', '"')
#         received_transferred = received_transferred.replace('\\"', '"')
#         joints_in = joints_in.replace('\\"', '"')
#         joints_out = joints_out.replace('\\"', '"')
#         footage = footage.replace('\\"', '"')
#         attachment = attachment.replace('\\"', '"')
#         manufacturer = manufacturer.replace('\\"', '"')
#         rack = rack.replace('\\"', '"')
#         c_datetime = c_datetime.replace('\\"', '"')
#
#         joints = 0
#         comp_footage = 0
#         try:
#             if joints_in:
#                 joints = int(joints_in)
#                 comp_footage = float(footage) if footage else 0
#             elif joints_out:
#                 joints = -int(joints_out)
#                 comp_footage = -float(footage) if footage else 0
#         except ValueError:
#             pass
#
#         date = c_date
#         if date == "0000-00-00":
#             date = "1970-01-01"
#
#         try:
#             product_dict[product_id].rack = rack_id
#             product_dict[product_id].save()
#
#             try:
#                 with open("pdf/" + attachment, "rb") as file:
#                     InventoryEntry.objects.create(
#                         product=product_dict[product_id],
#                         date=date,
#                         rr=rr,
#                         po=po,
#                         afe=afe,
#                         carrier=carrier,
#                         received_transferred=received_transferred,
#                         footage=comp_footage,
#                         joints=joints,
#                         attachment=SimpleUploadedFile(
#                             attachment, file.read(), content_type="application/pdf"
#                         ),
#                         manufacturer=manufacturer,
#                     )
#             except (FileNotFoundError, IsADirectoryError):
#                 InventoryEntry.objects.create(
#                     product=product_dict[product_id],
#                     date=date,
#                     rr=rr,
#                     po=po,
#                     afe=afe,
#                     carrier=carrier,
#                     received_transferred=received_transferred,
#                     footage=comp_footage,
#                     joints=joints,
#                     manufacturer=manufacturer,
#                 )
#         except KeyError:
#             print(f"Error: Product {product_id} does not exist")
#             print(
#                 inventory_id,
#                 customer_id,
#                 product_id,
#                 c_date,
#                 rr,
#                 po,
#                 carrier,
#                 received_transferred,
#                 joints_in,
#                 joints_out,
#                 footage,
#                 attachment,
#                 manufacturer,
#                 rack,
#                 afe,
#                 added_by,
#                 c_datetime,
#             )
#
#     cursor.close()
#     return HttpResponse("Ok")


def outside_diameter_to_float(value: str):
    """
    Converts an outside diameter measurement such as "Casing 5 1/2"" to a float, uses imperial notation.
    :param value:
    :return:
    """
    segments = value.split(" ")
    measure = 0
    for segment in segments:
        # Skip segment if it has no numbers
        if segment.isalpha():
            continue

        # Calculate the length of the remainder
        try:
            multiplier = 12 if "'" in segment else 1
            segment = segment.replace("'", "").replace('"', "")
            if "/" in segment:
                numerator, denominator = segment.split("/")
                measure += (float(numerator) / float(denominator)) * multiplier
            else:
                measure += float(segment) * multiplier
        except ValueError:
            pass

    return measure


def migrate_db(request):
    # Ensure user is admin
    if not request.user.groups.filter(name="admin").exists():
        return HttpResponse(status=403)

    # Clear django database
    print("Clearing db...")
    User.objects.filter(~Q(username="admin")).delete()
    print("Done.")

    # Connect to database
    print("Connecting to old db...")
    db_filename = request.GET.get("file", "old.sqlite")
    db = sqlite3.connect(db_filename)
    cursor = db.cursor()

    # Building database
    customer_dict = {}
    product_dict = {}

    for customer_id, username, display_name, email, phone, password in cursor.execute(
        "SELECT user_id, username, full_name, email, work_phone, password_text FROM users",
    ).fetchall():
        if username == "admin":
            continue

        print(customer_id, username, display_name, email, phone, password)
        username = username.replace('\\"', '"')
        display_name = display_name.replace('\\"', '"')
        email = email.replace('\\"', '"')
        phone = phone.replace('\\"', '"')
        password = password.replace('\\"', '"')
        username = username.replace('\\"', '"')

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )
        group = Group.objects.get(name="customer")
        group.user_set.add(user)

        customer = Customer.objects.create(
            user=user,
            phone_number=phone,
            display_name=display_name,
        )
        customer_dict[customer_id] = customer

    entries = cursor.execute("SELECT * FROM store").fetchall()
    for i, (
        inventory_id,
        customer_id,
        product_id,
        c_date,
        rr,
        po,
        carrier,
        received_transferred,
        joints_in,
        joints_out,
        footage,
        attachment,
        manufacturer,
        rack,
        afe,
        added_by,
        c_datetime,
    ) in enumerate(entries):
        print(f"{i*100/len(entries):.2f}%")
        c_date = c_date.replace('\\"', '"')
        rr = rr.replace('\\"', '"')
        po = po.replace('\\"', '"')
        carrier = carrier.replace('\\"', '"')
        received_transferred = received_transferred.replace('\\"', '"')
        joints_in = joints_in.replace('\\"', '"')
        joints_out = joints_out.replace('\\"', '"')
        footage = footage.replace('\\"', '"')
        attachment = attachment.replace('\\"', '"')
        manufacturer = manufacturer.replace('\\"', '"')
        rack = rack.replace('\\"', '"')
        c_datetime = c_datetime.replace('\\"', '"')

        # -------------------------------------------------------------------------------------------- Generate customer
        if customer_id not in customer_dict:
            print("Missing customer", customer_id)
            continue
        customer = customer_dict[customer_id]

        # --------------------------------------------------------------------------------------------- Generate product
        if product_id not in product_dict:
            try:
                od, weight, end_type, grade, coating, foreman = cursor.execute(
                    "SELECT outside_diameter, ibs_per_foot, end_type, grade, coating, foreman FROM products WHERE product_id = ?",
                    (product_id,),
                ).fetchone()
            except TypeError:
                print("Skipped missing product", product_id)
                continue

            od = od.replace('\\"', '"')
            diameter = []
            product_type = []
            for ele in od.replace('\\"', '"').split(" "):
                if any(char.isdigit() for char in ele) or ele == "x":
                    diameter.append(ele)
                else:
                    product_type.append(ele)
            diameter = " ".join(diameter)
            product_type = " ".join(product_type)

            weight = weight.replace('\\"', '"')
            end_type = end_type.replace('\\"', '"')
            grade = grade.replace('\\"', '"')
            foreman = foreman.replace('\\"', '"')

            # Split grade column to extract data
            elements = grade.split(",")
            if len(elements) == 1:
                elements = grade.split(" ")
            elements = [ele.strip() for ele in elements if ele.strip() != ""]

            grade = ""
            coupling = ""
            pipe_range = ""
            condition = ""

            for element in elements:
                # Range
                if re.match(r"R-?\d+", element):
                    pipe_range = re.findall(r"R-?\d+", element)[0]

                # Condition
                elif re.match(r"(\w+)-Condition", element):
                    condition = re.findall(r"(\w+)-Condition", element)[0]
                elif any(i in element for i in ["New", "Unknown"]):
                    condition = element

                # Grade
                elif any(
                    [
                        i in element
                        for i in [
                            "J-55",
                            "L-80",
                            "Seah",
                            "P110",
                            "Grade",
                            "X52",
                            "X42",
                            "T95",
                            "CP80",
                            "Junk",
                            "N-80",
                            "HCP-",
                            "DP-API",
                            "P-110",
                        ]
                    ]
                ):
                    grade = element

                # Coupling
                elif any(
                    [
                        i in element
                        for i in [
                            "VAM",
                            "GBCD",
                            "BTC",
                            "DWC/",
                            "EUE",
                            "GB CD",
                            "ERW",
                            "Vamedge",
                            "PH6",
                            "LTC",
                            "TSH",
                            "STC",
                            "VA",
                            "Ultra",
                            "S135",
                            "STL",
                        ]
                    ]
                ):
                    coupling = element

            elements.append(end_type)
            remarks = ", ".join(elements)

            product = Product.objects.create(
                product_type=product_type,
                outside_diameter_text=diameter,
                outside_diameter=convert_inches(od),
                weight=convert_weight(weight),
                weight_text=weight,
                grade=grade,
                coupling=coupling,
                range=pipe_range,
                condition=condition,
                remarks=remarks,
                foreman=foreman,
                customer=customer,
                rack=rack,
            )
            product_dict[product_id] = product

        product = product_dict[product_id]

        # ------------------------------------------------------------------------------------------- Generate inventory
        joints = 0
        comp_footage = 0
        try:
            if joints_in:
                joints = int(joints_in)
                comp_footage = float(footage) if footage else 0
            elif joints_out:
                joints = -int(joints_out)
                comp_footage = -float(footage) if footage else 0
        except ValueError:
            pass

        date = c_date
        if date == "0000-00-00":
            date = "1970-01-01"

        try:
            with open("pdf/" + attachment, "rb") as file:
                InventoryEntry.objects.create(
                    product=product,
                    date=date,
                    rr=rr,
                    po=po,
                    afe=afe,
                    carrier=carrier,
                    received_transferred=received_transferred,
                    footage=comp_footage,
                    joints=joints,
                    attachment=SimpleUploadedFile(
                        attachment, file.read(), content_type="application/pdf"
                    ),
                    manufacturer=manufacturer,
                )
        except (FileNotFoundError, IsADirectoryError, PermissionError):
            InventoryEntry.objects.create(
                product=product_dict[product_id],
                date=date,
                rr=rr,
                po=po,
                afe=afe,
                carrier=carrier,
                received_transferred=received_transferred,
                footage=comp_footage,
                joints=joints,
                manufacturer=manufacturer,
            )

    for product_id, customer_id in cursor.execute(
        "SELECT product_id, customer_id FROM products"
    ).fetchall():
        if product_id not in product_dict or customer_id not in product_dict:
            continue
        product = product_dict[product_id]
        customer = customer_dict[customer_id]
        product.customer = customer
        product.save()

    cursor.close()
    return HttpResponse("Ok")


def tmp(request):
    tags = Tag.objects.all()
    for tag in tags:
        tag.name = tag.name.replace("_", " ").title()
        tag.save()
    return HttpResponse("Ok")