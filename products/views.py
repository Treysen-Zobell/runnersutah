from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.http import JsonResponse, FileResponse
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy

import re
from fractions import Fraction
from datetime import datetime

from customers.views import generate_excel
from inventory.models import InventoryEntry
from products.forms import ProductForm
from products.models import Product
from utils.mixins import GroupRequiredMixin


# Create your views here.
class ProductListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Product
    template_name = "products/list.html"
    group_required = ["admin"]
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ordering = self.request.GET.get("ordering", "product_type")
        context["ordering"] = ordering

        paginator = context["paginator"]
        page = context["page_obj"]
        page_range = paginator.get_elided_page_range(
            number=page.number, on_each_side=3, on_ends=1
        )
        context["page_range"] = page_range

        return context

    def get_ordering(self):
        ordering = self.request.GET.get("ordering", "product_type")
        return ordering


class ProductDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = Product
    template_name = "products/detail.html"
    group_required = ["admin"]


class ProductCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Product
    template_name = "products/create.html"
    form_class = ProductForm
    group_required = ["admin"]

    def get_success_url(self):
        return self.request.GET.get("next", reverse_lazy("products:list"))

    def form_valid(self, form):
        response = super().form_valid(form)

        # Generate outside diameter measure if possible
        if form.cleaned_data["outside_diameter_text"]:
            self.object.outside_diameter = convert_inches(
                form.cleaned_data["outside_diameter_text"]
            )

        # Generate weight measure if possible
        if form.cleaned_data["weight_text"]:
            self.object.weight = convert_weight(form.cleaned_data["weight_text"])

        self.object.save()
        return response


class ProductUpdateView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Product
    template_name = "products/update.html"
    form_class = ProductForm
    group_required = ["admin"]

    def get_success_url(self):
        return self.request.GET.get("next", reverse_lazy("products:list"))

    def form_valid(self, form):
        response = super().form_valid(form)

        # Generate outside diameter measure if possible
        if form.cleaned_data["outside_diameter_text"]:
            self.object.outside_diameter = convert_inches(
                form.cleaned_data["outside_diameter_text"]
            )

        # Generate weight measure if possible
        if form.cleaned_data["weight_text"]:
            self.object.weight = convert_weight(form.cleaned_data["weight_text"])

        self.object.save()
        return response


@login_required
@require_POST
def delete_product(request, pk):
    if request.user.groups.filter(name="admin").exists():
        customer = Product.objects.get(pk=pk)
        customer.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
def load_products(request):
    customer_id = request.GET.get("customer")
    products = Product.objects.none()
    if customer_id:
        products = Product.objects.filter(customer_id=customer_id).order_by("rack")
    return render(request, "generic/dropdown_options.html", {"options": products})


def convert_inches(text: str) -> float:
    match = re.search(r"\b\d+\s*\d*/?\d*\b", text)
    if match:
        value = 0.0
        for measure in match.group(0).split():
            if "/" in measure:
                value += float(Fraction(measure))
            else:
                value += float(measure)
        return value
    else:
        return 0.0


def convert_weight(text: str) -> float:
    print(text)
    value = 0.0
    for measure in re.sub(r"[^0-9/.]", "", text).split():
        print(measure)
        if "/" in measure:
            print(measure.split("/"))
            value += float(measure.split("/")[0])
        else:
            value += float(measure)
    return value


@login_required
def download_product_list_sheet(request):
    ordering = request.GET.get("ordering", "product_type")
    products = Product.objects.all().order_by(ordering)

    labels = [
        "Product Type",
        "Outside Diameter",
        "Lbs Per Ft",
        "Grade",
        "CPLG",
        "Range",
        "Condition",
        "Remarks",
        "Foreman",
    ]
    rows = [
        (
            product.product_type,
            product.outside_diameter_text,
            product.weight_text,
            product.grade,
            product.coupling,
            product.range,
            product.condition,
            product.remarks,
            product.foreman,
        )
        for product in products
    ]

    file = generate_excel(labels, rows)
    response = FileResponse(file)
    response["Content-Type"] = "application/ms-excel"
    response["Content-Disposition"] = f"attachment; filename=products.xlsx"
    return response
