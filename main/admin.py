from django.contrib import admin
from .models import Ledger, Item, Person, Order, OrderItem
# # Register your models here.
admin.site.register(Ledger)
admin.site.register(Item)
admin.site.register(Person)
admin.site.register(Order)
admin.site.register(OrderItem)