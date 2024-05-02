import io

from django.contrib.auth.decorators import login_required
from django.db.models import Value, Case, IntegerField, When, F
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from common.utils import generate_excel
from customers.models import Customer
from products.models import Product
from .forms import InventoryForm
from .models import InventoryChange, InventoryCurrent
from common.utils import GoogleDrive, outside_diameter_to_float


@login_required
def load_products(request):
    """
    Gets the products associated with the selected customer
    :param request:
    :return:
    """
    customer_id = request.GET.get("customer")
    products = Product.objects.filter(customer_id=customer_id)
    print(products)
    return render(request, "inventory/dropdown_options.html", {"options": products})


@login_required
def download_inventory_table(request):
    inventory_changes = InventoryChange.objects.all()
    labels = [
        "Date",
        "R.R# OR REL#",
        "P.O# OR B/L#",
        "AFE",
        "Carrier",
        "Joints In",
        "Joints Out",
    ]
    rows = [
        (
            change.date.strftime("%m/%d/%Y"),
            change.rr,
            change.po,
            change.afe,
            change.carrier,
            change.joints if change.joints >= 0 else "",
            "" if change.joints >= 0 else -change.joints,
        )
        for change in inventory_changes
    ]

    file = generate_excel(labels, rows)
    response = FileResponse(file)
    response["Content-Type"] = "application/ms-excel"
    response["Content-Disposition"] = f"attachment; filename=inventory.xlsx"
    return response


@login_required
def index(request):
    order_by = request.GET.get("order_by", "date")
    order_dir = "-" if request.GET.get("order_dir", "desc") == "asc" else ""

    # Sorts joints major into +/- and minor by value to keep avoid blank entries at the top
    if order_by in ("joints_in", "joints_out"):
        positive_condition = Value(1) if order_by == "joints_in" else Value(2)
        negative_condition = Value(1) if order_by == "joints_out" else Value(2)
        sorted_objects = InventoryChange.objects.annotate(
            positive_negative=Case(
                When(joints__gte=0, then=positive_condition),
                When(joints__lt=0, then=negative_condition),
                output_field=IntegerField(),
            )
        )
        inventory = sorted_objects.order_by("positive_negative", order_dir + "joints")

    elif order_by == "outside_diameter":
        inventory = InventoryChange.objects.all()
        inventory = sorted(
            inventory,
            key=lambda p: outside_diameter_to_float(p.product.outside_diameter),
        )
        if order_dir == "-":
            inventory = reversed(inventory)

    else:
        inventory = InventoryChange.objects.order_by(order_dir + order_by)

    paginator = Paginator(inventory, 20)
    page = request.GET.get("page", 1)
    try:
        inventory = paginator.page(page)
        page_range = paginator.get_elided_page_range(number=page)
    except PageNotAnInteger:
        inventory = paginator.page(1)
        page_range = paginator.get_elided_page_range(number=1)
    except EmptyPage:
        inventory = paginator.page(paginator.num_pages)
        page_range = paginator.get_elided_page_range(number=paginator.num_pages)

    order_dir = "asc" if order_dir == "-" else "desc"
    context = {
        "inventory_list": inventory,
        "order_by": order_by,
        "order_dir": order_dir,
        "page_range": page_range,
        "page": page,
    }
    return render(request, "inventory/index.html", context)


@login_required
def detail(request, inventory_id: str):
    inventory = get_object_or_404(InventoryChange, pk=inventory_id)
    context = {"inventory": inventory}
    return render(request, "inventory/detail.html", context)


@login_required
def add(request):
    if request.method == "POST":
        form = InventoryForm(request.POST, request.FILES)
        if form.is_valid():
            # Process fields to convert joints in/out and footage to +/- values
            joints_multiplier = 1 if form.cleaned_data["joints_in"] else -1
            joints = joints_multiplier * (
                form.cleaned_data["joints_in"] or form.cleaned_data["joints_out"]
            )
            footage = joints_multiplier * form.cleaned_data["footage"]

            # Upload attachment to Google Drive if a file was selected and get file ID
            attachment_id = ""
            if form.cleaned_data["attachment_id"]:
                file = form.cleaned_data["attachment_id"]
                drive = GoogleDrive()
                attachment_id = drive.upload_file(file)

            # Create and save inventory change
            inventory = InventoryChange.objects.create(
                customer=form.cleaned_data["customer"],
                product=form.cleaned_data["product"],
                date=form.cleaned_data["date"],
                rr=form.cleaned_data["rr"],
                po=form.cleaned_data["po"],
                afe=form.cleaned_data["afe"],
                carrier=form.cleaned_data["carrier"],
                received_transferred=form.cleaned_data["received_transferred"],
                joints=joints,
                footage=footage,
                attachment_id=attachment_id,
                rack_id=form.cleaned_data["rack_id"],
            )
            inventory.save()

            if "submit" in request.POST:
                return redirect("inventory:index")

            form = InventoryForm()

    else:
        form = InventoryForm()

    return render(request, "inventory/add.html", {"form": form})


@login_required
def edit(request, inventory_id: str):
    inventory = get_object_or_404(InventoryChange, pk=inventory_id)
    if request.method == "POST":
        form = InventoryForm(request.POST, request.FILES)
        if form.is_valid():
            # Process fields to convert joints in/out and footage to +/- values
            joints_multiplier = 1 if form.cleaned_data["joints_in"] else -1
            joints = joints_multiplier * (
                form.cleaned_data["joints_in"] or form.cleaned_data["joints_out"]
            )
            footage = joints_multiplier * form.cleaned_data["footage"]

            # Delete old attachment and upload new attachment to Google Drive if a new file
            # was selected and save the new file ID
            if form.cleaned_data["attachment_id"]:
                drive = GoogleDrive()

                attachment_id = inventory.attachment_id
                if attachment_id:
                    drive.delete_file(attachment_id)

                file = form.cleaned_data["attachment_id"]
                inventory.attachment_id = drive.upload_file(file)

            # Save inventory change
            inventory.customer = form.cleaned_data["customer"]
            inventory.product = form.cleaned_data["product"]
            inventory.date = form.cleaned_data["date"]
            inventory.rr = form.cleaned_data["rr"]
            inventory.po = form.cleaned_data["po"]
            inventory.afe = form.cleaned_data["afe"]
            inventory.carrier = form.cleaned_data["carrier"]
            inventory.received_transferred = form.cleaned_data["received_transferred"]
            inventory.joints = joints
            inventory.footage = footage
            inventory.rack_id = form.cleaned_data["rack_id"]
            inventory.save()

            if "submit" in request.POST:
                return redirect("inventory:index")

            form = InventoryForm()

    else:
        form = InventoryForm(
            initial={
                "customer": inventory.customer,
                "product": inventory.product,
                "date": inventory.date,
            }
        )
        form.fields["rr"].initial = inventory.rr
        form.fields["po"].initial = inventory.po
        form.fields["afe"].initial = inventory.afe
        form.fields["carrier"].initial = inventory.carrier
        form.fields["received_transferred"].initial = inventory.received_transferred
        if inventory.joints >= 0:
            form.fields["joints_in"].initial = inventory.joints
            form.fields["joints_out"].initial = 0
        else:
            form.fields["joints_in"].initial = 0
            form.fields["joints_out"].initial = -inventory.joints
        form.fields["footage"].initial = abs(inventory.footage)
        form.fields["rack_id"].initial = inventory.rack_id

        form.fields["product"].queryset = Product.objects.filter(
            customer_id=inventory.customer
        )

    return render(
        request, "inventory/edit.html", {"form": form, "inventory_id": inventory_id}
    )


@login_required
def delete(request, inventory_id: str):
    inventory = get_object_or_404(InventoryChange, pk=inventory_id)

    # Delete file from Google Drive
    attachment_id = inventory.attachment_id
    drive = GoogleDrive()
    drive.delete_file(attachment_id)

    inventory.delete()

    return redirect("inventory:index")


@login_required
def download_attachment(request, inventory_id: str):
    inventory = get_object_or_404(InventoryChange, pk=inventory_id)

    # Download file from Google Drive
    drive = GoogleDrive()
    file = drive.download_file(inventory.attachment_id)
    file = io.BytesIO(file)

    # Return file download
    response = FileResponse(file)
    response["Content-Type"] = "application/pdf"
    response["Content-Disposition"] = (
        f"attachment; filename={inventory.attachment_id}.pdf"
    )
    return response


@login_required
def report(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)

    order_by = request.GET.get("order_by", "outside_diameter_inches")
    order_dir = "-" if request.GET.get("order_dir", "desc") == "asc" else ""

    if order_by in ("joints_in", "joints_out"):
        positive_condition = Value(1) if order_by == "joints_in" else Value(2)
        negative_condition = Value(1) if order_by == "joints_out" else Value(2)
        sorted_objects = InventoryCurrent.objects.filter(customer=customer).annotate(
            positive_negative=Case(
                When(joints__gte=0, then=positive_condition),
                When(joints__lt=0, then=negative_condition),
                output_field=IntegerField(),
            )
        )
        inventory_current = sorted_objects.order_by(
            "positive_negative", order_dir + "joints"
        )

    elif order_by in (
        "outside_diameter_inches",
        "weight",
        "grade",
        "coupling",
        "range",
        "condition",
        "remarks",
    ):
        inventory_current = (
            InventoryCurrent.objects.filter(customer=customer)
            .annotate(s=F(f"product__{order_by}"))
            .order_by(order_dir + "s")
        )

    else:
        inventory_current = InventoryCurrent.objects.filter(customer=customer).order_by(
            order_dir + order_by
        )

    paginator = Paginator(inventory_current, 20)
    page = request.GET.get("page", 1)
    try:
        inventory_current = paginator.page(page)
        page_range = paginator.get_elided_page_range(number=page)
    except PageNotAnInteger:
        inventory_current = paginator.page(1)
        page_range = paginator.get_elided_page_range(number=1)
    except EmptyPage:
        inventory_current = paginator.page(paginator.num_pages)
        page_range = paginator.get_elided_page_range(number=paginator.num_pages)

    order_dir = "asc" if order_dir == "-" else "desc"
    context = {
        "inventory_list": inventory_current,
        "order_by": order_by,
        "order_dir": order_dir,
        "customer_name": customer.display_name,
        "customer_id": customer_id,
        "page_range": page_range,
        "page": page,
    }
    return render(request, "inventory/report.html", context)


@login_required
def download_report_table(request, customer_id: str):
    inventory_changes = InventoryChange.objects.all()
    labels = [
        "Outside Diameter",
        "Lbs Per Ft",
        "Grade",
        "CPLG",
        "Range",
        "Condition",
        "Remarks",
        "Rack#",
        "Joints",
        "Footage",
    ]

    customer = get_object_or_404(Customer, pk=customer_id)
    inventory_current = InventoryCurrent.objects.filter(customer=customer)

    order_by = request.GET.get("order_by", "outside_diameter")
    order_dir = "-" if request.GET.get("order_dir", "desc") == "asc" else ""
    if order_by in (
        "outside_diameter",
        "weight",
        "grade",
        "coupling",
        "range",
        "condition",
        "remarks",
    ):
        inventory_current = inventory_current.annotate(
            s=F(f"product__{order_by}")
        ).order_by(f"s")
    else:
        inventory_current = inventory_current.order_by(order_dir + order_by)

    rows = [
        (
            inventory.product.outside_diameter,
            inventory.product.weight,
            inventory.product.grade,
            inventory.product.coupling,
            inventory.product.range,
            inventory.product.condition,
            inventory.product.remarks,
            inventory.rack_id,
            inventory.joints,
            inventory.footage,
            inventory.product.foreman,
        )
        for inventory in inventory_current
    ]

    file = generate_excel(labels, rows)
    response = FileResponse(file)
    response["Content-Type"] = "application/ms-excel"
    response["Content-Disposition"] = f"attachment; filename=inventory.xlsx"
    return response


@login_required
def report_detail(request, customer_id: str, product_id: str):
    # Get inventory changes sorted by date
    customer = get_object_or_404(Customer, pk=customer_id)
    product = get_object_or_404(Product, pk=product_id)
    inventory_changes = (
        InventoryChange.objects.filter(customer=customer)
        .filter(product=product)
        .order_by("date")
    )

    # Calculate historical joint and footage totals
    joints_history = {}
    footage_history = {}
    joints_total = 0
    footage_total = 0
    for change in inventory_changes:
        joints_total += change.joints
        footage_total += change.footage
        joints_history[change.id] = joints_total
        footage_history[change.id] = footage_total

    # Sort historical changes by column labels
    order_by = request.GET.get("order_by", "date")
    order_dir = "-" if request.GET.get("order_dir", "desc") == "asc" else ""

    if order_by in ("joints_in", "joints_out"):
        positive_condition = Value(1) if order_by == "joints_in" else Value(2)
        negative_condition = Value(1) if order_by == "joints_out" else Value(2)
        sorted_objects = (
            InventoryChange.objects.filter(customer=customer)
            .filter(product=product)
            .annotate(
                positive_negative=Case(
                    When(joints__gte=0, then=positive_condition),
                    When(joints__lt=0, then=negative_condition),
                    output_field=IntegerField(),
                )
            )
        )
        inventory_current = sorted_objects.order_by(
            "positive_negative", order_dir + "joints"
        )

    elif order_by in ("outside_diameter",):
        inventory_current = inventory_changes.annotate(
            s=F(f"product__{order_by}")
        ).order_by(f"s")

    else:
        inventory_current = inventory_changes.order_by(order_dir + order_by)

    paginator = Paginator(inventory_current, 20)
    page = request.GET.get("page", 1)
    try:
        inventory_current = paginator.page(page)
        page_range = paginator.get_elided_page_range(number=page)
    except PageNotAnInteger:
        inventory_current = paginator.page(1)
        page_range = paginator.get_elided_page_range(number=1)
    except EmptyPage:
        inventory_current = paginator.page(paginator.num_pages)
        page_range = paginator.get_elided_page_range(number=paginator.num_pages)

    order_dir = "asc" if order_dir == "-" else "desc"
    context = {
        "inventory_list": inventory_current,
        "joints_history": joints_history,
        "footage_history": footage_history,
        "order_by": order_by,
        "order_dir": order_dir,
        "customer_name": customer.display_name,
        "customer_id": customer_id,
        "product_id": product_id,
        "page_range": page_range,
        "page": page,
    }
    return render(request, "inventory/report_detail.html", context)


@login_required
def download_report_detail_table(request, customer_id: str, product_id: str):
    inventory_changes = InventoryChange.objects.all()
    labels = [
        "Date",
        "AFE",
        "R.R OR REL#",
        "P.O OR B/L#",
        "Carrier",
        "Received from Transferred to",
        "In",
        "Out",
        "Footage",
        "Manufacturer",
        "Rack#",
        "Joints",
        "Footage",
    ]

    # Get inventory changes sorted by date
    customer = get_object_or_404(Customer, pk=customer_id)
    product = get_object_or_404(Product, pk=product_id)
    inventory_changes = (
        InventoryChange.objects.filter(customer=customer)
        .filter(product=product)
        .order_by("date")
    )

    # Calculate historical joint and footage totals
    joints_history = {}
    footage_history = {}
    joints_total = 0
    footage_total = 0
    for change in inventory_changes:
        joints_total += change.joints
        footage_total += change.footage
        joints_history[change.id] = joints_total
        footage_history[change.id] = footage_total

    # Sort historical changes by column labels
    order_by = request.GET.get("order_by", "date")
    order_dir = "-" if request.GET.get("order_dir", "desc") == "asc" else ""

    if order_by in ("joints_in", "joints_out"):
        positive_condition = Value(1) if order_by == "joints_in" else Value(2)
        negative_condition = Value(1) if order_by == "joints_out" else Value(2)
        sorted_objects = InventoryChange.objects.annotate(
            positive_negative=Case(
                When(joints__gte=0, then=positive_condition),
                When(joints__lt=0, then=negative_condition),
                output_field=IntegerField(),
            )
        )
        inventory_current = sorted_objects.order_by(
            "positive_negative", order_dir + "joints"
        )

    elif order_by in ("outside_diameter",):
        inventory_current = inventory_changes.annotate(
            s=F(f"product__{order_by}")
        ).order_by(f"s")

    else:
        inventory_current = inventory_changes.order_by(order_dir + order_by)

    rows = [
        (
            inventory.date.strftime("%m/%d/%Y"),
            inventory.afe,
            inventory.rr,
            inventory.po,
            inventory.carrier,
            inventory.received_transferred,
            inventory.joints if inventory.joints >= 0 else "",
            "" if inventory.joints >= 0 else -inventory.joints,
            abs(inventory.footage),
            inventory.manufacturer,
            inventory.rack_id,
            joints_history[inventory.id],
            abs(footage_history[inventory.id]),
        )
        for inventory in inventory_current
    ]

    file = generate_excel(labels, rows)
    response = FileResponse(file)
    response["Content-Type"] = "application/ms-excel"
    response["Content-Disposition"] = f"attachment; filename=inventory.xlsx"
    return response
