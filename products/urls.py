from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="list"),
    path("detail/<int:pk>/", views.ProductDetailView.as_view(), name="detail"),
    path("create/", views.ProductCreateView.as_view(), name="create"),
    path("update/<int:pk>/", views.ProductUpdateView.as_view(), name="update"),
    path("load_products/", views.load_products, name="load_products"),
    path("delete/<int:pk>/", views.delete_product, name="delete"),
    path("download_table/", views.download_product_list_sheet, name="download_table"),
]
