# Generated by Django 5.0.4 on 2024-04-18 06:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("customers", "0001_initial"),
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="InventoryChange",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date", models.DateField()),
                ("rr", models.TextField(blank=True)),
                ("po", models.TextField(blank=True)),
                ("afe", models.TextField(blank=True)),
                ("carrier", models.TextField(blank=True)),
                ("received_transferred", models.TextField(blank=True)),
                ("joints", models.IntegerField()),
                ("footage", models.FloatField()),
                ("attachment_id", models.TextField(blank=True)),
                ("rack_id", models.TextField(blank=True)),
                ("manufacturer", models.TextField(blank=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customers.customer",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="InventoryCurrent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("last_updated", models.DateField()),
                ("joints", models.IntegerField()),
                ("footage", models.FloatField()),
                ("rack_id", models.TextField(blank=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="customers.customer",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="products.product",
                    ),
                ),
            ],
        ),
    ]