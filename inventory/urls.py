from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.InventoryEntryListView.as_view(), name="list"),
    path("detail/<int:pk>/", views.InventoryEntryDetailView.as_view(), name="detail"),
    path("create/", views.InventoryEntryCreateView.as_view(), name="create"),
    path("update/<int:pk>/", views.InventoryEntryUpdateView.as_view(), name="update"),
    path("delete/<int:pk>/", views.delete_inventory_entry, name="delete"),
    path("download_table/", views.download_inventory_list_sheet, name="download_table"),
    path(
        "customer_report/<int:customer_id>/",
        views.CustomerReportListView.as_view(),
        name="customer_report",
    ),
    path(
        "customer_report/<int:customer_id>/download_table/",
        views.download_customer_report_sheet,
        name="download_customer_report_table",
    ),
    path(
        "product_report/<int:product_id>/",
        views.ProductReportListView.as_view(),
        name="product_report",
    ),
    path(
        "product_report/<int:product_id>/download_table/",
        views.download_product_report_sheet,
        name="download_product_report_sheet",
    ),
    path(
        "zero_out/<int:product_id>/",
        views.zero_out_product,
        name="zero_out",
    ),
]
