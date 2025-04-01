from django.shortcuts import render

# Create your views here.
from rest_framework import status, generics
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework import viewsets
from .models import Product, Category, Brand,Cart,Order
from .serializers import ProductSerializer, CategorySerializer, BrandSerializer,CartSerializer,OrderSerializer,PaymentSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .models import Payment, Order,OrderItem
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, Payment
from .serializers import PaymentSerializer
from django.db import transaction
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Order, OrderItem, Cart

from rest_framework.exceptions import PermissionDenied
import stripe
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, Payment  # Ensure your models are imported

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = (MultiPartParser, FormParser)  # Enable image uploads

class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)  # Only show user's cart items

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            raise serializers.ValidationError({"error": "Your cart is empty!"})

        with transaction.atomic():
            shipping_address = serializer.validated_data.get("shipping_address")
            status = serializer.validated_data.get("status", "Pending")  # Default to 'Pending'

            order = Order.objects.create(user=user, shipping_address=shipping_address, status=status)

            order_items = [
                OrderItem(order=order, product=item.product, quantity=item.quantity)
                for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            order.total_amount = order.calculate_total_price()
            order.save(update_fields=['total_amount'])

            cart_items.delete()

            self.send_order_confirmation_email(order)

    def perform_update(self, serializer):
        """Handle order updates and send emails when status changes."""
        order = self.get_object()

        # Check if the user is an admin before allowing the status update
        if not self.request.user.is_staff:
            raise PermissionDenied("Only admins can update the order status.")

        previous_status = order.status  # Store previous status
        instance = serializer.save()

        # Send email when order is Shipped or Delivered
        if previous_status != instance.status:
            if instance.status == 'Shipped':
                self.send_shipped_email(instance)
            elif instance.status == 'Delivered':
                self.send_delivered_email(instance)

    def send_order_confirmation_email(self, order):
        """Send email when an order is placed."""
        subject = f"Order Confirmation - Order #{order.id}"
        message = f"Dear {order.user.username},\n\nYour order #{order.id} has been placed successfully.\nStatus: {order.status}\nShipping Address: {order.shipping_address}\nTotal Amount: ₹{order.total_amount}\n\nPlease pay your amount so shipped fast \n\n Thank you for shopping with us!"
        
        send_mail(subject, message, settings.EMAIL_HOST_USER, [order.user.email], fail_silently=False)

    def send_shipped_email(self, order):
        """Send email when an order is shipped."""
        subject = f"Your Order #{order.id} Has Been Shipped!"
        message = f"Dear {order.user.username},\n\nYour order #{order.id} has been shipped and is on its way!\nStatus: {order.status}\n\nThank you for shopping with us!"
        
        send_mail(subject, message, settings.EMAIL_HOST_USER, [order.user.email], fail_silently=False)

    def send_delivered_email(self, order):
        """Send email when an order is delivered."""
        subject = f"Order #{order.id} Delivered!"
        message = f"Dear {order.user.username},\n\nYour order #{order.id} has been delivered successfully!\nStatus: {order.status}\n\nThank you for shopping with us!"
        
        send_mail(subject, message, settings.EMAIL_HOST_USER, [order.user.email], fail_silently=False)


stripe.api_key = settings.STRIPE_SECRET_KEY  # Set your Stripe secret key

class StripeCheckoutView(APIView):
    def post(self, request):
        try:
            # Get the order ID and payment method ID from the request data
            order_id = request.data.get("order_id")
            payment_method_id = request.data.get("payment_method_id")  # Payment method ID from frontend

            if not payment_method_id:
                return Response({"error": "Payment method ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the order from the database
            order = Order.objects.get(id=order_id)

            # Create a PaymentIntent and confirm the payment using the payment method
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Amount in cents
                currency="aud",  # Set currency to AUD (Australian Dollar)
                payment_method=payment_method_id,  # The payment method ID from frontend
                confirmation_method='manual',  # Manual confirmation for flexibility
                confirm=True,  # Automatically confirm the payment
                return_url="https://yourdomain.com/success",  # URL for successful payment
            )

            # Save payment details in your database
            payment = Payment.objects.create(
                order=order,
                payment_method="card",  # Assuming card payment
                transaction_id=intent["id"],
                payment_status="Completed",  # Update payment status
            )

            # Update order status to "Shipped"
            order.status = "Shipped"
            order.save()

            # Respond with the success message
            return Response({
                "message": "Payment successful!",
                "payment_id": payment.id,
                "order_status": order.status,
                "payment_intent_status": intent["status"]
            }, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except stripe.error.CardError as e:
            return Response({"error": f"Card error: {e.user_message}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET  # Your webhook secret

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # Contains a stripe.PaymentIntent object

        # Payment has been confirmed, update order status
        order_id = payment_intent['metadata']['order_id']  # Assuming you stored the order_id in metadata
        order = Order.objects.get(id=order_id)
        order.status = "Shipped"
        order.save()

        # # Send confirmation email
        # send_order_confirmation_email(order)

    return JsonResponse({"status": "success"}, status=200)