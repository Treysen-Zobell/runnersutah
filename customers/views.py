from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout

from customers.models import Customer
from customers.forms import RegisterForm, EditForm, EditPasswordForm


app_name = "customers"


# Create your views here.
@login_required
def customer_list(request):
    order_by = request.GET.get("order_by", "display_name")
    order_dir = "-" if request.GET.get("order_dir", "asc") == "desc" else ""
    customers = Customer.objects.order_by(order_dir + order_by)
    context = {
        "customer_list": customers,
        "order_by": order_by,
        "order_dir": order_dir,
    }
    return render(request, "customers/customer_list.html", context)


@login_required
def detail(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)
    context = {"customer": customer}
    return render(request, "customers/customer_detail.html", context)


@login_required
def user_register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            customer = Customer.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                email=form.cleaned_data["email"],
                phone_nr=form.cleaned_data["phone_nr"],
                display_name=form.cleaned_data["display_name"],
                status="Inactive",
            )
            customer.save()
            return redirect("customers:customer_list")

    else:
        form = RegisterForm()

    return render(request, "customers/register.html", {"form": form})


@login_required
def user_edit(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == "POST":
        form = EditForm(request.POST, instance=customer)
        if form.is_valid():
            customer.username = form.cleaned_data["username"]
            customer.email = form.cleaned_data["email"]
            customer.phone_nr = form.cleaned_data["phone_nr"]
            customer.display_name = form.cleaned_data["display_name"]
            customer.save()
            return redirect("customers:customer_list")

    else:
        form = EditForm()
        form.fields["display_name"].initial = customer.display_name
        form.fields["username"].initial = customer.username
        form.fields["email"].initial = customer.email
        form.fields["phone_nr"].initial = customer.phone_nr

    return render(
        request,
        "customers/edit_customer.html",
        {"form": form, "customer_id": customer_id},
    )


@login_required
def user_edit_password(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == "POST":
        form = EditPasswordForm(customer, request.POST)
        if form.is_valid():
            customer.set_password(form.cleaned_data["new_password1"])
            customer.save()
            return redirect("customers:customer_list")

    else:
        form = EditPasswordForm(customer)

    return render(
        request,
        "customers/change_password.html",
        {"form": form, "customer_id": customer_id},
    )


@login_required
def user_delete(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)
    customer.delete()
    return redirect("customers:customer_list")


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
