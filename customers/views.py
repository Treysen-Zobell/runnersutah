from io import BytesIO
from typing import List, Any
import xlsxwriter

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.forms import SetPasswordForm
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,
    UpdateView,
    FormView,
)
from django.contrib.auth.models import Group, User

from customers.forms import CreateCustomerForm, UpdateCustomerForm, EmailFormSet
from customers.models import Customer, Email, Tag
from utils.mixins import GroupRequiredMixin


# Create your views here.
class CustomerListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Customer
    template_name = "customers/list.html"
    group_required = ["admin"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ordering = self.request.GET.get("ordering", "display_name")
        context["ordering"] = ordering

        return context

    def get_ordering(self):
        ordering = self.request.GET.get("ordering", "display_name")
        return ordering


class CustomerDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = Customer
    template_name = "customers/detail.html"
    group_required = ["admin"]


class CustomerCreateView(LoginRequiredMixin, GroupRequiredMixin, CreateView):
    model = Customer
    template_name = "customers/create.html"
    form_class = CreateCustomerForm
    success_url = reverse_lazy("customers:list")
    group_required = ["admin"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["email_formset"] = EmailFormSet(self.request.POST)
        else:
            context["email_formset"] = EmailFormSet()
        return context

    def form_valid(self, form):
        email_formset = EmailFormSet(self.request.POST)

        if email_formset.is_valid():
            response = super().form_valid(form)

            # Add customer to customers group
            group = Group.objects.get(name="customer")
            self.object.groups.add(group)

            # Create customer
            customer = Customer.objects.create(
                display_name=form.cleaned_data["display_name"],
                phone_number=form.cleaned_data["phone_number"],
                user=self.object,
            )

            # Create mailing list
            for email_form in email_formset:
                email_address = email_form.cleaned_data.get("email")
                tags = email_form.cleaned_data.get("tags")
                if email_address:
                    email = Email.objects.create(
                        address=email_address, customer=customer
                    )
                    for tag in tags:
                        Tag.objects.create(name=tag, email=email)

            return response
        else:
            return self.form_invalid(form)


# class CustomerUpdateView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
#     model = Customer
#     template_name = "customers/update.html"
#     form_class = UpdateCustomerForm
#     success_url = reverse_lazy("customers:list")
#     group_required = ["admin"]
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#
#         # Get current mailing list
#         customer_id = self.kwargs.get("pk")
#
#         email_addresses = []
#         for email_address in Email.objects.filter(customer_id=customer_id):
#             tags = Tag.objects.filter(email_id=email_address.id)
#             tag_names = [t.name for t in tags]
#             tags_text = ", ".join(tag_names)
#             email_addresses.append([email_address.address, tags_text])
#         context["email_list"] = email_addresses
#
#         return context
#
#     def form_valid(self, form):
#         response = super().form_valid(form)
#
#         # Delete old mailing list
#         customer_id = self.kwargs["pk"]
#         Email.objects.filter(customer_id=customer_id).delete()
#
#         # Build new mailing list
#         email_list = self.request.POST.getlist("email_list")
#         tag_list = self.request.POST.getlist("tag_list")
#         for email_text, tags_text in zip(email_list, tag_list):
#             for email_text2 in email_text.split(","):
#                 email_text2 = email_text2.strip()
#                 email = Email.objects.create(
#                     address=email_text2, customer_id=customer_id
#                 )
#                 for tag_text in tags_text.split(","):
#                     tag_text = tag_text.strip()
#                     Tag.objects.create(name=tag_text, email=email)
#
#         # Save email
#         email_address = form.cleaned_data.get("email")
#         customer = Customer.objects.get(id=customer_id)
#         customer.user.email = email_address
#         customer.user.save()
#
#         return response
#
#     def get_initial(self):
#         initial = super().get_initial()
#
#         initial["email"] = self.object.user.email
#
#         return initial


class CustomerUpdateView(LoginRequiredMixin, GroupRequiredMixin, UpdateView):
    model = Customer
    template_name = "customers/update.html"
    form_class = UpdateCustomerForm
    success_url = reverse_lazy("customers:list")
    group_required = ["admin"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["email_formset"] = EmailFormSet(
                self.request.POST, queryset=Email.objects.filter(customer=self.object)
            )
        else:
            context["email_formset"] = EmailFormSet(
                queryset=Email.objects.filter(customer=self.object)
            )
        return context

    def form_valid(self, form):
        email_formset = EmailFormSet(self.request.POST)

        if email_formset.is_valid():
            response = super().form_valid(form)

            # Delete old mailing list
            customer_id = self.kwargs["pk"]
            Email.objects.filter(customer_id=customer_id).delete()

            # Create mailing list
            for email_form in email_formset:
                email_address = email_form.cleaned_data.get("address")
                tags = email_form.cleaned_data.get("tags")
                if email_address:
                    email = Email.objects.create(
                        address=email_address, customer_id=customer_id
                    )
                    for tag in tags:
                        Tag.objects.create(name=tag, email=email)

            # Save email
            email_address = form.cleaned_data.get("email")
            customer = Customer.objects.get(id=customer_id)
            customer.user.email = email_address
            customer.user.save()

            return response
        else:
            return self.form_invalid(form)

    def get_initial(self):
        initial = super().get_initial()

        initial["email"] = self.object.user.email

        return initial


class CustomerUpdatePasswordView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    model = Customer
    template_name = "customers/update_password.html"
    form_class = SetPasswordForm
    success_url = reverse_lazy("customers:login")

    def test_func(self):
        user = self.request.user
        user_to_change = get_object_or_404(User, pk=self.kwargs["pk"])
        return user == user_to_change or user.groups.filter(name="admin").exists()

    def form_valid(self, form):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        user.set_password(form.cleaned_data["new_password1"])
        user.save()

        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = get_object_or_404(User, pk=self.kwargs["pk"])
        return kwargs


class CustomerUpdateEmailView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    fields = ["email"]
    template_name = "customers/update_email.html"
    success_url = reverse_lazy("customers:list")

    def test_func(self):
        user = self.request.user
        user_to_change = get_object_or_404(User, pk=self.kwargs["pk"])
        return user == user_to_change or user.groups.filter(name="admin").exists()

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Email address updated successfully.")
        return super().form_valid(form)


@login_required
@require_POST
def delete_customer(request, pk):
    if request.user.groups.filter(name="admin").exists():
        customer = Customer.objects.get(pk=pk)
        customer.user.delete()
        customer.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
def download_customer_list_sheet(request):
    ordering = request.GET.get("ordering", "display_name")
    customers = Customer.objects.all().order_by(ordering)

    labels = ["Full Name", "Username", "Email", "Status"]
    rows = [
        (
            customer.display_name,
            customer.user.username,
            customer.user.email,
            customer.status,
        )
        for customer in customers
    ]

    file = generate_excel(labels, rows)
    response = FileResponse(file)
    response["Content-Type"] = "application/ms-excel"
    response["Content-Disposition"] = f"attachment; filename=customers.xlsx"
    return response


def generate_excel(column_labels: List[str], rows: List[Any]):
    file = BytesIO()

    workbook = xlsxwriter.Workbook(file, {"in_memory": True})
    worksheet = workbook.add_worksheet()

    header_row_format = workbook.add_format({"bold": True})

    worksheet.set_row(0, 25)
    worksheet.insert_image(
        0, 0, "static/resources/runners_logo.png", {"x_scale": 0.1, "y_scale": 0.1}
    )
    worksheet.write_row(1, 0, column_labels, header_row_format)
    for i in range(len(rows)):
        worksheet.write_row(i + 2, 0, rows[i])

    worksheet.autofit()
    workbook.close()

    file.seek(0, 0)
    return file
