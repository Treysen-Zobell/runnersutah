from django.contrib import admin

from customers.models import Customer, NotificationGroup, Email

admin.site.register(Customer)
admin.site.register(NotificationGroup)
admin.site.register(Email)
