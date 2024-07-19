from django.contrib import admin

from customers.models import Customer, Email, Tag

# Register your models here.
admin.site.register(Customer)
admin.site.register(Email)
admin.site.register(Tag)
