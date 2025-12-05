from django.contrib import admin

from inventory.models import (
    StorageLocation,
    InventoryChangeTemplate,
    InventoryChangeTemplateField,
    InventoryTransaction,
    InventoryChangeLine,
    InventoryChangeFieldValue,
)

admin.site.register(StorageLocation)
admin.site.register(InventoryChangeTemplate)
admin.site.register(InventoryChangeTemplateField)
admin.site.register(InventoryTransaction)
admin.site.register(InventoryChangeLine)
admin.site.register(InventoryChangeFieldValue)
