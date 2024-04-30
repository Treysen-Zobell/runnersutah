from django.urls import path

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.index, name="index"),
    path("detail/<str:customer_id>", views.detail, name="detail"),
    path("add", views.add, name="add"),
    path("edit/<str:customer_id>", views.edit, name="edit"),
    path("edit/<str:user_id>/password", views.edit_password, name="edit_password"),
    path("edit/<str:user_id>/username", views.edit_username, name="edit_username"),
    path("edit/<str:user_id>/email", views.edit_email, name="edit_email"),
    path("delete/<str:customer_id>", views.delete, name="delete"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path(
        "download/customer_table",
        views.download_customer_table,
        name="download_customer_table",
    ),
    path("migrate", views.migrate, name="migrate"),
]
