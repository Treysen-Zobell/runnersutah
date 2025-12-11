from django.urls import path

from customers.views import CustomerCreateView, add_form

app_name = "customers"

urlpatterns = [
    path("create/", CustomerCreateView.as_view(), name="customer_create"),
    path("partials/add_form/", add_form, name="add_form"),
]
