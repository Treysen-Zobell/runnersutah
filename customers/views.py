import io

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.http import FileResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import auth
import pandas as pd

from customers.models import Customer
from customers.forms import (
    RegisterForm,
    EditForm,
    EditPasswordForm,
    EditUsernameForm,
    EditEmailForm,
)

app_name = "customers"


@login_required
def download_customer_table(request):
    customers = Customer.objects.all()
    display_names = []
    usernames = []
    emails = []
    statuses = []
    for customer in customers:
        display_names.append(customer.display_name)
        usernames.append(customer.username)
        emails.append(customer.email)
        statuses.append(customer.status)
    df = pd.DataFrame(
        {
            "Full Name": display_names,
            "Username": usernames,
            "Email": emails,
            "Status": statuses,
        }
    )
    file = io.BytesIO()
    df.to_excel(file, index=False)
    file.seek(0, 0)

    response = FileResponse(file)
    response["Content-Type"] = "application/ms-excel"
    response["Content-Disposition"] = f"attachment; filename=customers.xlsx"
    return response


@login_required
def index(request):
    order_by = request.GET.get("order_by", "display_name")
    order_dir = "-" if request.GET.get("order_dir", "desc") == "asc" else ""
    customers = Customer.objects.order_by(order_dir + order_by)
    context = {
        "customer_list": customers,
        "order_by": order_by,
        "order_dir": order_dir,
    }
    return render(request, "customers/index.html", context)


@login_required
def detail(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)
    context = {"customer": customer}
    return render(request, "customers/detail.html", context)


@login_required
def add(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            customer = Customer.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                email=form.cleaned_data["email"],
                phone_number=form.cleaned_data["phone_number"],
                display_name=form.cleaned_data["display_name"],
                status="Inactive",
            )
            customer.save()
            return redirect("customers:index")

    else:
        form = RegisterForm()

    return render(request, "customers/add.html", {"form": form})


@login_required
def edit(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == "POST":
        form = EditForm(request.POST, instance=customer)
        if form.is_valid():
            customer.username = form.cleaned_data["username"]
            customer.email = form.cleaned_data["email"]
            customer.phone_number = form.cleaned_data["phone_number"]
            customer.display_name = form.cleaned_data["display_name"]
            customer.save()
            return redirect("customers:index")

    else:
        form = EditForm()
        form.fields["display_name"].initial = customer.display_name
        form.fields["username"].initial = customer.username
        form.fields["email"].initial = customer.email
        form.fields["phone_number"].initial = customer.phone_number

    return render(
        request,
        "customers/edit.html",
        {"form": form, "customer_id": customer_id},
    )


@login_required
def edit_password(request, user_id: str):
    customer = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        form = EditPasswordForm(customer, request.POST)
        if form.is_valid():
            customer.set_password(form.cleaned_data["new_password1"])
            customer.save()
            return redirect("customers:index")

    else:
        form = EditPasswordForm(customer)

    return render(
        request,
        "customers/change_password.html",
        {"form": form, "user_id": user_id},
    )


@login_required
def edit_username(request, user_id: str):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        form = EditUsernameForm(request.POST, instance=user)
        if form.is_valid():
            user.username = form.cleaned_data["username"]
            user.save()
            return redirect("user:customer_list")

    else:
        form = EditUsernameForm(instance=user)

    return render(
        request,
        "customers/change_username.html",
        {"form": form, "user_id": user_id},
    )


@login_required
def edit_email(request, user_id: str):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        form = EditEmailForm(request.POST, instance=user)
        if form.is_valid():
            user.email = form.cleaned_data["email"]
            user.save()
            return redirect("user:customer_list")

    else:
        form = EditEmailForm(instance=user)

    return render(
        request,
        "customers/change_email.html",
        {"form": form, "user_id": user_id},
    )


@login_required
def delete(request, customer_id: str):
    customer = get_object_or_404(Customer, pk=customer_id)
    customer.delete()
    return redirect("customers:index")


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)

        if form.is_valid():
            user = auth.authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                auth.login(request, user)
                return redirect("customers:index")

        return render(
            request,
            "customers/login.html",
            {"form": form, "error_message": "Incorrect username or password"},
        )

    else:
        form = AuthenticationForm()

    return render(request, "customers/login.html", {"form": form})


@login_required
def logout(request):
    auth.logout(request)
    return login(request)
