from django.urls import path, include

from . import views

app_name = "user"

urlpatterns = [
    path(
        "editpassword/",
        views.user_edit_password,
        name="edit_password",
    ),
    path("editusername/", views.user_edit_username, name="edit_username"),
    path("editemail/", views.user_edit_email, name="edit_email"),
]
