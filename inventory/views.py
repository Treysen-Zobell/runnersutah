import re
from typing import List, Optional
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
    Sum,
    When,
    Value,
    Case,
    IntegerField,
    Window,
    F,
    Subquery,
    OuterRef,
)
from django.http import JsonResponse, FileResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.core.mail import EmailMessage

from customers.models import Customer, Email, Tag
from customers.views import generate_excel
from inventory.forms import InventoryEntryForm
from inventory.models import InventoryEntry
from products.models import Product
from runnersutah import settings
from utils.mixins import GroupRequiredMixin


# Create your views here.
class InventoryEntryListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = InventoryEntry
    template_name = "inventory/list.html"
    group_required = ["admin"]
    paginate_by = 100

    def get_queryset(self):
        queryset = super().get_queryset()

        # Annotate the queryset to calculate sort_joints_in and sort_joints_out based on joints
        ordering = self.request.GET.get("ordering", "date")

        if ordering in ("joints_in", "-joints_in", "joints_out", "-joints_out"):
            order_dir = "-" if ordering.startswith("-") else ""
            positive_condition = (
                Value(1) if ordering in ("joints_in", "-joints_in") else Value(2)
            )
            negative_condition = (
                Value(1) if ordering in ("joints_out", "-joints_out") else Value(2)
            )
            queryset = queryset.annotate(
                joints_major=Case(
                    When(joints__gte=0, then=positive_condition),
                    When(joints__lt=0, then=negative_condition),
                    output_field=IntegerField(),
                )
            )

            queryset = queryset.order_by("joints_major", f"{order_dir}joints")
        else:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Modify context data to calculate joints_in and joints_out based on joints
        for obj in context["object_list"]:
            if obj.joints is not None:
                if obj.joints >= 0:
                    obj.joints_in = obj.joints
                    obj.joints_out = ""
                else:
                    obj.joints_in = ""
                    obj.joints_out = -obj.joints
                    obj.footage = -obj.footage

        # Build elided paginator
        paginator = context["paginator"]
        page = context["page_obj"]
        page_range = paginator.get_elided_page_range(
            number=page.number, on_each_side=3, on_ends=1
        )
        context["page_range"] = page_range

        ordering = self.request.GET.get("ordering", "date")
        context["ordering"] = ordering

        return context


class InventoryEntryDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = InventoryEntry
    template_name = "inventory/detail.html"
    group_required = ["admin"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Modify context data to calculate joints_in and joints_out based on joints
        if context["object"].joints is not None:
            if context["object"].joints >= 0:
                context["object"].joints_in = context["object"].joints
                context["object"].joints_out = ""
            else:
                context["object"].joints_in = ""
                context["object"].joints_out = -context["object"].joints
                context["object"].footage = -context["object"].footage

        return context


class InventoryEntryCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = InventoryEntry
    template_name = "inventory/create.html"
    form_class = InventoryEntryForm
    group_required = ["admin"]

    def get_success_url(self):
        return self.request.GET.get("next", reverse_lazy("inventory:list"))

    def form_valid(self, form):
        response = super().form_valid(form)

        # Redirect to self if add another is requested
        if "save_add_another" in self.request.POST:
            self.success_url = reverse_lazy("inventory:create")

        # Send notification email if requested
        if form.cleaned_data.get("send_email_update") == "yes":
            send_product_report_sheet(self.object)

        return response


class InventoryEntryUpdateView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = InventoryEntry
    template_name = "inventory/update.html"
    form_class = InventoryEntryForm
    group_required = ["admin"]

    def get_success_url(self):
        return self.request.GET.get("next", reverse_lazy("inventory:list"))

    def get_initial(self):
        initial = super().get_initial()
        entry = self.get_object()
        if entry.joints >= 0:
            initial["joints_in"] = entry.joints
            initial["joints_out"] = ""
        else:
            initial["joints_in"] = ""
            initial["joints_out"] = -entry.joints
            initial["footage"] = -entry.footage
        return initial

    def form_valid(self, form):
        # Convert joints in/out to joints +/-
        joints_in = form.cleaned_data["joints_in"]
        joints_out = form.cleaned_data["joints_out"]
        if joints_in is not None:
            form.instance.joints = joints_in
        else:
            form.instance.joints = -joints_out

        response = super().form_valid(form)

        # Send notification email if requested
        if form.cleaned_data.get("send_email_update") == "yes":
            send_product_report_sheet(self.object)

        return response


class CustomerReportListView(LoginRequiredMixin, ListView):
    template_name = "inventory/customer_report.html"

    def get_queryset(self):
        customer_id = self.kwargs.get("customer_id")
        ordering = self.request.GET.get("ordering", "outside_diameter")

        # queryset = (
        #     InventoryEntry.objects.filter(product__customer_id=customer_id)
        #     .values("product_id", *[f"product__{n.name}" for n in Product._meta.fields])
        #     .annotate(total_joints=Sum("joints"), total_footage=Sum("footage"))
        #     .order_by(ordering)
        # )

        queryset = (
            Product.objects.filter(customer_id=customer_id)
            .annotate(
                total_joints=Subquery(
                    InventoryEntry.objects.filter(product=OuterRef("pk"))
                    .values("product")
                    .annotate(total_joints=Sum("joints"))
                    .values("total_joints")
                ),
                total_footage=Subquery(
                    InventoryEntry.objects.filter(product=OuterRef("pk"))
                    .values("product")
                    .annotate(total_footage=Sum("footage"))
                    .values("total_footage")
                ),
            )
            .order_by(ordering)
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Modify context data to calculate joints_in and joints_out based on joints
        ordering = self.request.GET.get("ordering", "outside_diameter")
        context["ordering"] = ordering

        customer_name = Customer.objects.get(
            id=self.kwargs.get("customer_id")
        ).display_name
        context["customer_name"] = customer_name
        context["customer_id"] = self.kwargs.get("customer_id")

        return context


class ProductReportListView(LoginRequiredMixin, ListView):
    template_name = "inventory/product_report.html"

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        queryset = InventoryEntry.objects.filter(product_id=product_id)

        # Annotate the queryset to calculate sort_joints_in and sort_joints_out based on joints
        ordering = self.request.GET.get("ordering", "date")

        if ordering in ("joints_in", "-joints_in", "joints_out", "-joints_out"):
            order_dir = "-" if ordering.startswith("-") else ""
            positive_condition = (
                Value(1) if ordering in ("joints_in", "-joints_in") else Value(2)
            )
            negative_condition = (
                Value(1) if ordering in ("joints_out", "-joints_out") else Value(2)
            )
            queryset = queryset.annotate(
                joints_major=Case(
                    When(joints__gte=0, then=positive_condition),
                    When(joints__lt=0, then=negative_condition),
                    output_field=IntegerField(),
                )
            )

            queryset = queryset.order_by("joints_major", f"{order_dir}joints")
        else:
            queryset = queryset.order_by(ordering)

        queryset = queryset.annotate(
            running_total_joints=Window(
                expression=Sum("joints"), order_by=[F("date").asc(), F("id").asc()]
            ),
            running_total_footage=Window(
                expression=Sum("footage"), order_by=[F("date").asc(), F("id").asc()]
            ),
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Modify context data to calculate joints_in and joints_out based on joints
        ordering = self.request.GET.get("ordering", "date")
        context["ordering"] = ordering

        product = Product.objects.get(id=self.kwargs.get("product_id"))
        context["product_name"] = str(product)
        context["customer_name"] = product.customer.display_name
        context["product_id"] = product.id

        for obj in context["object_list"]:
            if obj.joints is not None:
                if obj.joints >= 0:
                    obj.joints_in = obj.joints
                    obj.joints_out = ""
                else:
                    obj.joints_in = ""
                    obj.joints_out = -obj.joints
                    obj.footage = -obj.footage

        return context


@login_required
@require_POST
def delete_inventory_entry(request, pk):
    if request.user.groups.filter(name="admin").exists():
        customer = InventoryEntry.objects.get(pk=pk)
        customer.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


def convert_joints_context(object_list: List[InventoryEntry]):
    for obj in object_list:
        if obj.joints is not None:
            if obj.joints >= 0:
                obj.joints_in = obj.joints
                obj.joints_out = ""
            else:
                obj.joints_in = ""
                obj.joints_out = -obj.joints
                obj.footage = -obj.footage
    return object_list


@login_required
def download_inventory_list_sheet(request):
    ordering = request.GET.get("ordering", "date")
    inventory_entries = InventoryEntry.objects.all().order_by(ordering)

    labels = [
        "Date",
        "R.R# OR REL#",
        "P.O# OR B/L#",
        "AFE",
        "Carrier",
        "Joints In",
        "Joints Out",
        "Footage",
    ]
    rows = [
        (
            entry.date.strftime("%m/%d/%Y"),
            entry.rr,
            entry.po,
            entry.afe,
            entry.carrier,
            entry.joints if entry.joints >= 0 else "",
            "" if entry.joints >= 0 else -entry.joints,
            abs(entry.footage),
        )
        for entry in inventory_entries
    ]

    file = generate_excel(labels, rows)
    response = FileResponse(file)
    response["Content-Type"] = "application/ms-excel"
    response["Content-Disposition"] = f"attachment; filename=inventory.xlsx"
    return response


@login_required
def download_customer_report_sheet(request, customer_id: int):
    ordering = request.GET.get("ordering", "product__outside_diameter")
    queryset = (
        InventoryEntry.objects.filter(product__customer_id=customer_id)
        .values("product_id", *[f"product__{n.name}" for n in Product._meta.fields])
        .annotate(total_joints=Sum("joints"), total_footage=Sum("footage"))
        .order_by(ordering)
    )

    labels = [
        "Product Type",
        "Outside Diameter",
        "Lbs Per Ft",
        "Grade",
        "Coupling",
        "Range",
        "Condition",
        "Rack",
        "Total Joints",
        "Footage",
        "Foreman",
    ]
    rows = [
        (
            q.get("product__product_type"),
            q.get("product__outside_diameter_text"),
            q.get("product__weight_text"),
            q.get("product__grade"),
            q.get("product__coupling"),
            q.get("product__range"),
            q.get("product__condition"),
            q.get("product__rack"),
            q.get("total_joints"),
            f'{q.get("total_footage"):.3f}',
            q.get("product__foreman"),
        )
        for q in queryset
    ]

    file = generate_excel(labels, rows)
    response = FileResponse(file)
    response["Content-Type"] = "application/ms-excel"
    response["Content-Disposition"] = f"attachment; filename=customer_report.xlsx"
    return response


@login_required
def download_product_report_sheet(request, product_id: int):
    ordering = request.GET.get("ordering", "date")
    file = generate_product_report(product_id, ordering)
    response = FileResponse(file)
    response["Content-Type"] = "application/ms-excel"
    response["Content-Disposition"] = f"attachment; filename=product_report.xlsx"
    return response


def generate_product_report(product_id: int, ordering: Optional[str] = None):
    queryset = InventoryEntry.objects.filter(product_id=product_id)
    if not ordering:
        ordering = "-date"

    if ordering in ("joints_in", "-joints_in", "joints_out", "-joints_out"):
        order_dir = "-" if ordering.startswith("-") else ""
        positive_condition = (
            Value(1) if ordering in ("joints_in", "-joints_in") else Value(2)
        )
        negative_condition = (
            Value(1) if ordering in ("joints_out", "-joints_out") else Value(2)
        )
        queryset = queryset.annotate(
            joints_major=Case(
                When(joints__gte=0, then=positive_condition),
                When(joints__lt=0, then=negative_condition),
                output_field=IntegerField(),
            )
        )

        queryset = queryset.order_by("joints_major", f"{order_dir}joints")
    else:
        queryset = queryset.order_by(ordering)

    queryset = queryset.annotate(
        running_total_joints=Window(expression=Sum("joints"), order_by=F("date").asc()),
        running_total_footage=Window(
            expression=Sum("footage"), order_by=F("date").asc()
        ),
    )

    labels = [
        "Date",
        "AFE",
        "R.R# OR REL#",
        "P.O# OR B/L#",
        "Carrier",
        "In",
        "Out",
        "Footage",
        "Total Joints",
        "Total Footage",
        "Manufacturer",
        "Rack#",
    ]
    rows = [
        (
            entry.date.strftime("%m/%d/%Y"),
            entry.afe,
            entry.rr,
            entry.po,
            entry.carrier,
            entry.joints if entry.joints >= 0 else "",
            "" if entry.joints >= 0 else -entry.joints,
            f"{abs(entry.footage):.3f}",
            entry.running_total_joints,
            entry.running_total_footage,
            entry.manufacturer,
            entry.product.rack,
        )
        for entry in queryset
    ]

    file = generate_excel(labels, rows)
    return file


def send_product_report_sheet(inventory_entry: InventoryEntry):
    print("Sending product report")
    report = generate_product_report(inventory_entry.product.id, ordering="-date")

    product_elements = [
        inventory_entry.product.outside_diameter_text,
        inventory_entry.product.weight_text,
        inventory_entry.product.product_type,
        inventory_entry.product.coupling,
        inventory_entry.product.condition,
    ]
    product_elements = [p for p in product_elements if p]
    product_desc = ", ".join(product_elements)

    subject_elements = [product_desc]
    if inventory_entry.rr:
        subject_elements.append(inventory_entry.rr)
    if inventory_entry.po:
        subject_elements.append(inventory_entry.po)
    if inventory_entry.received_transferred:
        subject_elements.append(inventory_entry.received_transferred)
    subject = ", ".join(subject_elements)

    body = "An update has been made to your inventory. If you have an questions or concerns please contact Runners Inc (435) 722-4259 or reply to this email.\n\nThank you!"

    mailing_list = []
    for email_list in Email.objects.filter(
        customer_id=inventory_entry.product.customer.id
    ):
        print("Email list", email_list)
        tags = Tag.objects.filter(email_id=email_list.id)
        tags = [tag.name for tag in tags]
        print("Tags", tags)
        if any(
            [
                tag.lower() == "any"
                or re.match(tag.lower(), inventory_entry.product.product_type.lower())
                for tag in tags
            ]
        ):
            for email in email_list.address.split(","):
                mailing_list.append(email)

    email = EmailMessage(
        subject,
        body,
        from_email=settings.EMAIL_HOST_USER,
        to=mailing_list,
        attachments=[("report.xlsx", report.read(), "application/ms-excel")],
    )
    email.send()


@login_required
def zero_out_product(request, product_id: int):
    entries = InventoryEntry.objects.filter(product_id=product_id)
    total_footage = 0
    total_joints = 0
    for entry in entries:
        total_joints += entry.joints
        total_footage += entry.footage
    InventoryEntry.objects.create(
        product_id=product_id,
        date=datetime.now(),
        joints=-total_joints,
        footage=-total_footage,
        carrier="Zero Out",
    )
    return JsonResponse({"success": True})
