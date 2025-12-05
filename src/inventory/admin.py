from django.contrib import admin

from inventory.models import (
    StorageLocation,
    InventoryChangeTemplate,
    InventoryChangeTemplateField,
    InventoryChange,
    InventoryChangeFieldValue,
)

admin.site.register(StorageLocation)
admin.site.register(InventoryChangeTemplate)
admin.site.register(InventoryChangeTemplateField)
admin.site.register(InventoryChange)
admin.site.register(InventoryChangeFieldValue)
