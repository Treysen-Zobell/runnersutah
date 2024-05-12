from django.contrib import admin

from .models import Customer, Email, Tag

admin.site.register(Customer)
admin.site.register(Email)
admin.site.register(Tag)
