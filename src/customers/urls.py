from django.urls import path

from customers.views import CustomerCreateView, add_form, CustomerUpdateView, CustomerListView, CustomerDeleteView, \
    CustomerDetailView

app_name = "customers"

urlpatterns = [
    path("create/", CustomerCreateView.as_view(), name="customer_create"),
    path("<int:pk>/", CustomerDetailView.as_view(), name="customer_detail"),
    path("<int:pk>/update/", CustomerUpdateView.as_view(), name="customer_update"),
    path("<int:pk>/delete/", CustomerDeleteView.as_view(), name="customer_delete"),
    path("", CustomerListView.as_view(), name="customer_list"),
    path("partials/add_form/", add_form, name="add_form"),
]
