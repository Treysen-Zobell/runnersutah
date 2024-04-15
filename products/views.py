from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from products.models import Product
from products.forms import ProductForm


@login_required
def product_list(request):
    order_by = request.GET.get("order_by", "outside_diameter")
    order_dir = "-" if request.GET.get("order_dir", "desc") == "asc" else ""
    products = Product.objects.order_by(order_dir + order_by)
    context = {
        "product_list": products,
        "order_by": order_by,
        "order_dir": order_dir,
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
            product = Product.objects.create(form)
            # customer = Product.objects.create_user(
            #     username=form.cleaned_data["username"],
            #     password=form.cleaned_data["password1"],
            #     email=form.cleaned_data["email"],
            #     phone_nr=form.cleaned_data["phone_nr"],
            #     display_name=form.cleaned_data["display_name"],
            #     status="Inactive",
            # )
            # customer.save()
            return redirect("products:product_list")

    else:
        form = ProductForm()

    return render(request, "products/add.html", {"form": form})


@login_required
def product_edit(request, product_id: str):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            # customer = Product.objects.create_user(
            #     username=form.cleaned_data["username"],
            #     password=form.cleaned_data["password1"],
            #     email=form.cleaned_data["email"],
            #     phone_nr=form.cleaned_data["phone_nr"],
            #     display_name=form.cleaned_data["display_name"],
            #     status="Inactive",
            # )
            # customer.save()
            return redirect("products:product_list")

    else:
        form = ProductForm()

    return render(request, "products/edit.html", {"form": form})


@login_required
def product_delete(request, product_id: str):
    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    return redirect("products:product_list")
