from django.contrib import admin

from products.models import (
    ProductTemplate,
    ProductTemplateField,
    Product,
    ProductFieldValue,
)

admin.site.register(ProductTemplate)
admin.site.register(ProductTemplateField)
admin.site.register(Product)
admin.site.register(ProductFieldValue)
