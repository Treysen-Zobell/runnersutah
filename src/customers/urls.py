from django.urls import path

from customers.views import CustomerCreateView

urlpatterns = [
    path("create/", CustomerCreateView.as_view(), name="customer_create"),
]
