from django.urls import path, include

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:customer_id>/", views.detail, name="detail"),
]
