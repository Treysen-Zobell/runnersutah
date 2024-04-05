from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from customers.models import Customer
from customers.forms import RegisterForm


# Create your views here.
@login_required
def index(request):
    order_by = request.GET.get("order_by", "-display_name")
    customer_list = Customer.objects.order_by(order_by)
    context = {
        "customer_list": customer_list,
    }
    return render(request, "customers/index.html", context)


@login_required
def detail(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)
    context = {"customer": customer}
    return render(request, "customers/detail.html", context)


@login_required
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            return HttpResponse("well done")

    else:
        form = RegisterForm()

    return render(request, "customers/login.html", {"form": form})


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                return HttpResponse(f"you are logged in {user.username}")

        return render(
            request,
            "customers/login.html",
            {"form": form, "error_message": "Incorrect username or password"},
        )

    else:
        form = AuthenticationForm()

    return render(request, "customers/login.html", {"form": form})


def user_logout(request):
    logout(request)
    return user_login(request)
