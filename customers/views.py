from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404

from customers.models import Customer


# Create your views here.
def index(request):
    customer_list = Customer.objects.order_by('-display_name')
    context = {
        "customer_list": customer_list,
    }
    return render(request, "customers/index.html", context)


def detail(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)
    context = {
        "customer": customer
    }
    return render(request, "customers/detail.html", context)
