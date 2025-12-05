from django.contrib import admin

from inventory.models import (
    InventoryChangeTemplate,
    InventoryChangeTemplateField,
    InventoryChange,
    InventoryChangeFieldValue,
)

admin.site.register(InventoryChangeTemplate)
admin.site.register(InventoryChangeTemplateField)
admin.site.register(InventoryChange)
admin.site.register(InventoryChangeFieldValue)
