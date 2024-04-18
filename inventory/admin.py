from django.contrib import admin

from .models import InventoryChange, InventoryCurrent

admin.site.register(InventoryChange)
admin.site.register(InventoryCurrent)
