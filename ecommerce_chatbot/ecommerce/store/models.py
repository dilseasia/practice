# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from django.db import models, transaction
from django.core.mail import send_mail
from django.conf import settings
import stripe
from django.conf import settings
from django.db import models



class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True, related_name='products')
    stock_quantity = models.IntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Image upload
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey("store.Product", on_delete=models.CASCADE, related_name='cart_entries')
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"





User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_price(self):
        total = self.order_items.annotate(
            item_total=models.F('product__price') * models.F('quantity')
        ).aggregate(total=models.Sum('item_total'))['total']
        return total or 0  # Return 0 if no items exist

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if it's a new order

        super().save(*args, **kwargs)  # Save the order first

        # Update total amount only after order items are created
        if not is_new:
            self.total_amount = self.calculate_total_price()
            super().save(update_fields=['total_amount'])  # Update only total_amount

        # If the order status has changed to "Shipped", send an email
        if self.pk and self.status == "Shipped":
            self.send_shipped_email()

        # if is_new:
        #     transaction.on_commit(self.send_order_confirmation_email)

    def send_order_confirmation_email(self):
        """Send an email to the user when an order is placed"""
        subject = f"Order Confirmation - Order #{self.id}"
        message = f"Dear {self.user.username},\n\nThank you for your order!\n\nYour order details:\n- Order ID: {self.id}\n- Total Amount: ₹{self.total_amount}\n- Status: {self.status}\n- Shipping Address: {self.shipping_address}\n\nWe will notify you when your order is shipped.\n\nThank you for shopping with us!"

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Sender email
            [self.user.email],  # Recipient email
            fail_silently=False,
        )

    def send_shipped_email(self):
        """Send an email to the user when the order is shipped"""
        subject = f"Your Order #{self.id} has been Shipped"
        message = f"Dear {self.user.username},\n\nGood news! Your order has been shipped.\n\nOrder Details:\n- Order ID: {self.id}\n- Total Amount: ₹{self.total_amount}\n- Shipping Address: {self.shipping_address}\n\nThank you for shopping with us!"

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  # Sender email
            [self.user.email],  # Recipient email
            fail_silently=False,
        )

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"




    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"




class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Card'),
        ('paypal', 'PayPal'),
        ('upi', 'UPI'),
    ]

    id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    payment_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.payment_status}"
