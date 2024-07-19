from django.contrib.auth import views as auth_views
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import path, reverse_lazy

from . import views

app_name = "customers"

urlpatterns = [
    path("", views.CustomerListView.as_view(), name="list"),
    path("detail/<int:pk>/", views.CustomerDetailView.as_view(), name="detail"),
    path("create/", views.CustomerCreateView.as_view(), name="create"),
    path("update/<int:pk>/", views.CustomerUpdateView.as_view(), name="update"),
    path(
        "update_password/<int:pk>/",
        views.CustomerUpdatePasswordView.as_view(),
        name="update_password",
    ),
    path(
        "update_email/<int:pk>/",
        views.CustomerUpdateEmailView.as_view(),
        name="update_email",
    ),
    path("delete/<int:pk>/", views.delete_customer, name="delete"),
    path("download_table/", views.download_customer_list_sheet, name="download_table"),
    path(
        "password_reset/",
        PasswordResetView.as_view(
            template_name="customers/password_reset.html",
            success_url=reverse_lazy("customers:password_reset_done"),
            html_email_template_name="customers/password_reset_email.html",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        PasswordResetView.as_view(
            template_name="customers/password_reset_done.html",
            success_url=reverse_lazy("customers:password_reset_complete"),
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="customers/password_reset_confirm.html",
            success_url=reverse_lazy("customers:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="customers/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="customers/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(
            template_name="customers/logout.html", next_page=None
        ),
        name="logout",
    ),
]
