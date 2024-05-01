import io
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from products.models import Product
from products.forms import ProductForm
from common.utils import generate_excel, outside_diameter_to_float


@login_required
def download_product_table(request):
    products = Product.objects.all()
    labels = [
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
            product.outside_diameter,
            product.weight,
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


@login_required
def product_list(request):
    order_by = request.GET.get("order_by", "outside_diameter_inches")
    order_dir = "-" if request.GET.get("order_dir", "desc") == "asc" else ""
    products = Product.objects.order_by(order_dir + order_by)

    paginator = Paginator(products, 20)
    page = request.GET.get("page", 1)
    try:
        products = paginator.page(page)
        page_range = paginator.get_elided_page_range(number=page)
    except PageNotAnInteger:
        products = paginator.page(1)
        page_range = paginator.get_elided_page_range(number=1)
    except EmptyPage:
        product = paginator.page(paginator.num_pages)
        page_range = paginator.get_elided_page_range(number=paginator.num_pages)

    context = {
        "product_list": products,
        "order_by": order_by,
        "order_dir": order_dir,
        "page_range": page_range,
    }
    return render(request, "products/index.html", context)


@login_required
def product_detail(request, product_id: str):
    product = get_object_or_404(Product, pk=product_id)
    context = {"product": product}
    return render(request, "products/detail.html", context)


@login_required
def product_add(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = Product.objects.create(**form.cleaned_data)
            product.save()
            return redirect("products:index")

    else:
        form = ProductForm()

    return render(request, "products/add.html", {"form": form})


@login_required
def product_edit(request, product_id: str):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product.outside_diameter = form.cleaned_data["outside_diameter"]
            product.outside_diameter_inches = outside_diameter_to_float(
                form.cleaned_data["outside_diameter"]
            )
            product.weight = form.cleaned_data["weight"]
            product.grade = form.cleaned_data["grade"]
            product.coupling = form.cleaned_data["coupling"]
            product.range = form.cleaned_data["range"]
            product.condition = form.cleaned_data["condition"]
            product.remarks = form.cleaned_data["remarks"]
            product.customer_id = form.cleaned_data["customer_id"]
            product.save()

            return redirect("products:index")

    else:
        form = ProductForm()
        form.fields["outside_diameter"].initial = product.outside_diameter
        form.fields["weight"].initial = product.weight
        form.fields["grade"].initial = product.grade
        form.fields["coupling"].initial = product.coupling
        form.fields["range"].initial = product.range
        form.fields["condition"].initial = product.condition
        form.fields["remarks"].initial = product.remarks
        form.fields["customer_id"].initial = product.customer_id

    return render(
        request, "products/edit.html", {"form": form, "product_id": product_id}
    )


@login_required
def product_delete(request, product_id: str):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return redirect("products:index")
