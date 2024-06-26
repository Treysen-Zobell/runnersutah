import re
import sqlite3
from io import BytesIO

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group
from django.db.models import Q, F
from django.db.models.functions import Lower
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import auth
from django.views.generic.edit import FormView
from extra_views import InlineFormSetFactory, CreateWithInlinesView

from customers.models import Customer, Email, Tag
from customers.forms import (
    RegisterForm,
    EditForm,
    EditPasswordForm,
    EditUsernameForm,
    EditEmailForm,
)
from common.utils import generate_excel, GoogleDrive, outside_diameter_to_float
from inventory.models import InventoryChange, InventoryCurrent
from products.models import Product

app_name = "customers"


@login_required
def download_customer_table(request):
    customers = Customer.objects.all()
    labels = ["Full Name", "Username", "Email", "Status"]
    rows = [
        (
            customer.display_name,
            customer.user.username,
            customer.user.email,
            customer.status,
        )
        for customer in customers
    ]

    file = generate_excel(labels, rows)
    response = FileResponse(file)
    response["Content-Type"] = "application/ms-excel"
    response["Content-Disposition"] = f"attachment; filename=customers.xlsx"
    return response


@login_required
def index(request):
    order_by = request.GET.get("order_by", "display_name")
    order_dir = "-" if request.GET.get("order_dir", "desc") == "asc" else ""

    if order_by in ("username", "email"):
        customers = Customer.objects.annotate(s=Lower(F(f"user__{order_by}"))).order_by(
            order_dir + "s"
        )
    else:
        customers = Customer.objects.order_by(order_dir + order_by)

    paginator = Paginator(customers, 20)
    page = request.GET.get("page", 1)
    try:
        customers = paginator.page(page)
        page_range = paginator.get_elided_page_range(number=page)
    except PageNotAnInteger:
        customers = paginator.page(1)
        page_range = paginator.get_elided_page_range(number=1)
    except EmptyPage:
        customers = paginator.page(paginator.num_pages)
        page_range = paginator.get_elided_page_range(number=paginator.num_pages)

    order_dir = "asc" if order_dir == "-" else "desc"
    context = {
        "customer_list": customers,
        "order_by": order_by,
        "order_dir": order_dir,
        "page_range": page_range,
        "page": page,
    }
    return render(request, "customers/index.html", context)


@login_required
def detail(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)

    email_lines = []
    for email in list(Email.objects.filter(customer=customer)):
        tags = list(Tag.objects.filter(email=email))
        tags = [t.name for t in tags]
        tags = ", ".join(tags)
        email_lines.append((email.address, tags))

    context = {"customer": customer, "email_list": email_lines}
    return render(request, "customers/detail.html", context)


@login_required
def add(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # todo undo steps if anything fails
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                email=form.cleaned_data["email"],
            )

            group = Group.objects.get(name="customer")
            group.user_set.add(user)

            customer = Customer.objects.create(
                user=user,
                phone_number=form.cleaned_data["phone_number"],
                display_name=form.cleaned_data["display_name"],
                status="Inactive",
            )

            for email_text, tags_text in zip(
                request.POST.getlist("email_list"), request.POST.getlist("tag_list")
            ):
                email = Email.objects.create(address=email_text, customer=customer)
                for tag_text in tags_text.split(","):
                    tag_text = tag_text.strip()
                    Tag.objects.create(name=tag_text, email=email)

            return redirect("customers:index")

    else:
        form = RegisterForm()

    return render(request, "customers/add.html", {"form": form})


@login_required
def edit(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)

    if request.method == "POST":
        form = EditForm(request.POST, instance=customer)
        if form.is_valid():
            customer.user.username = form.cleaned_data["username"]
            customer.user.email = form.cleaned_data["email"]
            customer.phone_number = form.cleaned_data["phone_number"]
            customer.display_name = form.cleaned_data["display_name"]
            customer.save()

            Email.objects.filter(customer=customer).delete()
            for email_text, tags_text in zip(
                request.POST.getlist("email_list"), request.POST.getlist("tag_list")
            ):
                email = Email.objects.create(address=email_text, customer=customer)
                for tag_text in tags_text.split(","):
                    tag_text = tag_text.strip()
                    Tag.objects.create(name=tag_text, email=email)

            return redirect("customers:index")

    else:
        form = EditForm()
        form.fields["display_name"].initial = customer.display_name
        form.fields["username"].initial = customer.user.username
        form.fields["email"].initial = customer.user.email
        form.fields["phone_number"].initial = customer.phone_number

    email_lines = []
    for email in list(Email.objects.filter(customer=customer)):
        tags = list(Tag.objects.filter(email=email))
        tags = [t.name for t in tags]
        tags = ", ".join(tags)
        email_lines.append((email.address, tags))

    return render(
        request,
        "customers/edit.html",
        {
            "form": form,
            "customer_id": customer_id,
            "email_list": email_lines,
        },
    )


@login_required
def edit_password(request, user_id: str):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        form = EditPasswordForm(user, request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data["new_password1"])
            user.save()
            return redirect("customers:index")

    else:
        form = EditPasswordForm(user)

    return render(
        request,
        "customers/change_password.html",
        {"form": form, "user_id": user_id},
    )


@login_required
def edit_username(request, user_id: str):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        form = EditUsernameForm(request.POST, instance=user)
        if form.is_valid():
            user.username = form.cleaned_data["username"]
            user.save()
            return redirect("user:customer_list")

    else:
        form = EditUsernameForm(instance=user)

    return render(
        request,
        "customers/change_username.html",
        {"form": form, "user_id": user_id},
    )


@login_required
def edit_email(request, user_id: str):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        form = EditEmailForm(request.POST, instance=user)
        if form.is_valid():
            user.email = form.cleaned_data["email"]
            user.save()
            return redirect("user:customer_list")

    else:
        form = EditEmailForm(instance=user)

    return render(
        request,
        "customers/change_email.html",
        {"form": form, "user_id": user_id},
    )


@login_required
def delete(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)
    customer.delete()
    return redirect("customers:index")


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = auth.authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                auth.login(request, user)
                if user.groups.filter(name="admin").exists():
                    return redirect("customers:index")
                else:
                    return redirect("inventory:report", user.pk)

        return render(
            request,
            "customers/login.html",
            {"form": form, "error_message": "Incorrect username or password"},
        )

    else:
        form = AuthenticationForm()

    return render(request, "customers/login.html", {"form": form})


@login_required
def logout(request):
    auth.logout(request)
    return login(request)


@login_required
def migrate(request):
    old_db = sqlite3.connect("old_processed.sqlite3")
    old_db_cursor = old_db.cursor()

    InventoryCurrent.objects.all().delete()
    InventoryChange.objects.all().delete()
    Product.objects.all().delete()
    Customer.objects.all().delete()
    User.objects.filter(~Q(username="admin")).delete()

    customer_dict = {}
    product_dict = {}

    # Import customers from old DB
    old_users = old_db_cursor.execute("SELECT * FROM users").fetchall()
    for (
        user_id,
        username,
        display_name,
        email,
        phone,
        _,
        _,
        password,
        _,
        _,
        _,
        user_role,
        _,
    ) in old_users:
        if username == "admin":
            continue

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
            status="Inactive",
        )
        customer_dict[user_id] = customer

    # Import products from old DB
    old_products = old_db_cursor.execute("SELECT * FROM products").fetchall()
    for (
        product_id,
        od,
        _,
        weight,
        end_type,
        grade,
        coating,
        foreman,
        customer_id,
    ) in old_products:
        # Clean inputs
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

        try:
            weight = float(weight.replace("#", ""))
        except ValueError:
            weight = None

        product = Product.objects.create(
            product_type=product_type,
            outside_diameter=diameter,
            outside_diameter_inches=outside_diameter_to_float(od),
            weight=weight,
            grade=grade,
            coupling=coupling,
            range=pipe_range,
            condition=condition,
            remarks=remarks,
            foreman=foreman,
            customer_id=customer_dict[customer_id],
        )
        product_dict[product_id] = product

    drive = GoogleDrive()
    old_inventory = old_db_cursor.execute("SELECT * FROM store").fetchall()
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
    ) in enumerate(old_inventory):
        # print(f"{(i / len(old_inventory)) * 100:.2f}%")

        rack_id = old_db_cursor.execute(
            "SELECT coating FROM products WHERE product_id = ?", (product_id,)
        ).fetchone()
        if rack_id is None:
            print(f"Product {product_id} does not exist")
            rack_id = "default"
        else:
            rack_id = rack_id[0]

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

        # Upload attachment
        file_id = attachment
        # if attachment:
        #     try:
        #         filename = attachment
        #         with open("/home/treysenzobell/Downloads/pdf/" + filename, "rb") as f:
        #             file_id = drive.upload_file(f, name=inventory_id)
        #     except Exception as e:
        #         pass

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
            InventoryChange.objects.create(
                customer=customer_dict[customer_id],
                product=product_dict[product_id],
                date=date,
                rr=rr,
                po=po,
                afe=afe,
                carrier=carrier,
                received_transferred=received_transferred,
                footage=comp_footage,
                joints=joints,
                attachment_id=file_id,
                rack_id=rack_id,
                manufacturer=manufacturer,
            )
        except KeyError:
            print(f"Error: Product {product_id} does not exist")
            print(
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
            )

    old_db_cursor.close()

    return HttpResponse("OK")
