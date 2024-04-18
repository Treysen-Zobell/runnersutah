from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add, name="add"),
    path("get/<str:inventory_id>/", views.detail, name="detail"),
    path("edit/<str:inventory_id>/", views.edit, name="edit"),
    path(
        "download/attachment/<str:inventory_id>/",
        views.download_attachment,
        name="download_attachment",
    ),
    path("delete/<str:inventory_id>/", views.delete, name="delete"),
    path("report/<str:customer_id>/", views.report, name="report"),
    path(
        "report/<str:customer_id>/<str:product_id>",
        views.report_detail,
        name="report_detail",
    ),
    path("load_products/", views.load_products, name="load_products"),
]
