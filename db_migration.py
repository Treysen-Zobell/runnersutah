from customers.models import Customer
from products.models import Product
from inventory.models import InventoryChange
from common.utils import GoogleDrive

import sqlite3
import re


def main():
    old_db = sqlite3.connect("old_processed.sqlite3")
    old_db_cursor = old_db.cursor()

    customer_dict = {}
    product_dict = {}

    old_users = old_db_cursor.execute("SELECT * FROM users").fetchall()
    for (
        user_id,
        username,
        display_name,
        email,
        phone,
        address,
        _,
        password,
        _,
        created_date,
        modified_date,
        user_role,
        status,
    ) in old_users:
        customer = Customer.objects.create_user(
            username=username,
            password=password,
            email=email,
            phone_number=phone,
            display_name=display_name,
            status="Inactive",
        )
        customer_dict[user_id] = customer

    old_products = old_db_cursor.execute("SELECT * FROM products").fetchall()
    for (
        product_id,
        od,
        wall_thickness,
        weight,
        end_type,
        grade,
        coating,
        foreman,
        customer_id,
    ) in old_products:
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

        remarks = ", ".join(elements)

        if grade and coupling and pipe_range and condition and remarks:
            continue

        product = Product.objects.create(
            outside_diameter=od.replace('\\"', '"'),
            weight=weight,
            grade=grade,
            coupling=coupling,
            range=pipe_range,
            condition=condition,
            remarks=remarks.replace('\\"', '"'),
            foreman=foreman,
            customer_id=customer_dict[customer_id],
        )
        product_dict[product_id] = product

    drive = GoogleDrive()

    old_inventory = old_db_cursor.execute("SELECT * FROM store")
    for (
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
    ) in old_inventory:
        rack_id = old_db_cursor.execute(
            "SELECT coating FROM products WHERE product_id = ?", (product_id,)
        )

        # Upload attachment
        file_id = "NONE"
        # if attachment:
        #     try:
        #         filename = attachment
        #         with open(filename, "r") as f:
        #             file_id = drive.upload_file(f)
        #     except Exception as e:
        #         pass

        InventoryChange.objects.create(
            customer=customer_dict[customer_id],
            product=product_dict[product_id],
            date=c_date,
            rr=rr,
            po=po,
            afe=afe,
            carrier=carrier,
            received_transferred=received_transferred,
            footage=footage,
            attachment_id=file_id,
            rack_id=rack_id,
            manufacturer=manufacturer,
        )

    old_db_cursor.close()


if __name__ == "__main__":
    main()
