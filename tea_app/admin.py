from django.contrib import admin
from .models import Category, MenuItem, Milk, Cart, Order, OrderItem
# Register your models here.
admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Milk)

admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
