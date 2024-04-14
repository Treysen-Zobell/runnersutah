from django.urls import path, include

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.customer_list, name="customer_list"),
    path("get/<str:customer_id>/", views.detail, name="detail"),
    path("edit/<str:customer_id>/", views.user_edit, name="edit"),
    path(
        "editpassword/<str:customer_id>/",
        views.user_edit_password,
        name="edit_password",
    ),
    path("delete/<str:customer_id>/", views.user_delete, name="delete"),
    path("register/", views.user_register, name="register"),
    path("login/", views.user_login, name="user_login"),
    path("logout/", views.user_logout, name="user_logout"),
]
