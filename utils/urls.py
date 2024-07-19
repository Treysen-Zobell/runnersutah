from django.urls import path

from . import views

app_name = "utils"

urlpatterns = [
    path("generate_default/", views.populate_tables, name="generate_default"),
    path("login_redirect/", views.login_redirect, name="smart_group_redirect"),
    path("run_migration/", views.migrate_db, name="run_migration"),
    path(
        "tmp/",
        views.tmp,
        name="tmp",
    ),
]
