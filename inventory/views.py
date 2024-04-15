import io

from django.contrib.auth.decorators import login_required
from django.db.models import Value, Case, IntegerField, When
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect

from .models import ManifestUpdate
from .forms import InventoryForm
from .utils import GoogleDrive


@login_required
def index(request):
    order_by = request.GET.get("order_by", "date")
    order_dir = "-" if request.GET.get("order_dir", "desc") == "asc" else ""

    # Sorts joints major into +/- and minor by value to keep avoid blank entries at the top
    if order_by in ("joints_in", "joints_out"):
        positive_condition = Value(1) if order_by == "joints_in" else Value(2)
        negative_condition = Value(1) if order_by == "joints_out" else Value(2)
        sorted_objects = ManifestUpdate.objects.annotate(
            positive_negative=Case(
                When(joints__gte=0, then=positive_condition),
                When(joints__lt=0, then=negative_condition),
                output_field=IntegerField(),
            )
        )
        inventory = sorted_objects.order_by("positive_negative", order_dir + "joints")

    else:
        inventory = ManifestUpdate.objects.order_by(order_dir + order_by)

    context = {
        "inventory_list": inventory,
        "order_by": order_by,
        "order_dir": order_dir,
    }
    return render(request, "inventory/index.html", context)


@login_required
def detail(request, inventory_id: str):
    inventory = get_object_or_404(ManifestUpdate, pk=inventory_id)
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
            if form.cleaned_data["attachment"]:
                file = form.cleaned_data["attachment"]
                drive = GoogleDrive()
                attachment_id = drive.upload_file(file)

            # Create and save inventory change
            inventory = ManifestUpdate.objects.create(
                customer_id=form.cleaned_data["customer_id"],
                product_id=form.cleaned_data["product_id"],
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
    inventory = get_object_or_404(ManifestUpdate, pk=inventory_id)
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
            if form.cleaned_data["attachment"]:
                drive = GoogleDrive()

                attachment_id = inventory.attachment_id
                if attachment_id:
                    drive.delete_file(attachment_id)

                file = form.cleaned_data["attachment"]
                inventory.attachment_id = drive.upload_file(file)

            # Save inventory change
            inventory.customer_id = form.cleaned_data["customer_id"]
            inventory.product_id = form.cleaned_data["product_id"]
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
        form = InventoryForm()
        form.fields["customer_id"].initial = inventory.customer_id
        form.fields["product_id"].initial = inventory.product_id
        form.fields["date"].initial = inventory.date
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
            form.fields["joints_out"].initial = inventory.joints
        form.fields["footage"].initial = abs(inventory.footage)
        form.fields["rack_id"].initial = inventory.rack_id

    return render(
        request, "inventory/edit.html", {"form": form, "inventory_id": inventory_id}
    )


@login_required
def delete(request, inventory_id: str):
    inventory = get_object_or_404(ManifestUpdate, pk=inventory_id)

    # Delete file from Google Drive
    attachment_id = inventory.attachment_id
    drive = GoogleDrive()
    drive.delete_file(attachment_id)

    inventory.delete()
    return redirect("inventory:index")


@login_required
def download_attachment(request, inventory_id: str):
    inventory = get_object_or_404(ManifestUpdate, pk=inventory_id)

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
