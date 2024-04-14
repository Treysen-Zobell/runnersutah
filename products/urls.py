from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("<str:product_id>/", views.product_detail, name="detail"),
]
