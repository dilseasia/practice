from django.contrib import admin
from .models import CustomUser, Category, Brand, Product, Cart, Order, OrderItem, Payment

# Register your models
admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
