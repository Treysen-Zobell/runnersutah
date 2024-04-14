from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from products.models import Product


@login_required
def product_list(request):
    order_by = request.GET.get("order_by", "outside_diameter")
    order_dir = "-" if request.GET.get("order_dir", "asc") == "desc" else ""
    products = Product.objects.order_by(order_dir + order_by)
    context = {
        "product_list": products,
        "order_by": order_by,
        "order_dir": order_dir,
    }
    return render(request, "products/product_list.html", context)


@login_required
def product_detail(request, product_id: str):
    customer = get_object_or_404(Product, pk=product_id)
    context = {"product": customer}
    return render(request, "products/product_detail.html", context)

