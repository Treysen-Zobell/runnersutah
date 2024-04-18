from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="index"),
    path("add", views.product_add, name="add"),
    path("get/<str:product_id>/", views.product_detail, name="detail"),
    path("edit/<str:product_id>/", views.product_edit, name="edit"),
    path("delete/<str:product_id>/", views.product_delete, name="delete"),
    path(
        "download/product_table",
        views.download_product_table,
        name="download_product_table",
    ),
]
