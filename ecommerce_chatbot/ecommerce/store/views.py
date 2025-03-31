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

        with transaction.atomic():  # Ensure atomic transaction
            # Step 1: Create the Order
            order = serializer.save(user=user)

            # Step 2: Move Cart Items to OrderItems
            order_items = []
            for cart_item in cart_items:
                order_items.append(OrderItem(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity
                ))
            
            OrderItem.objects.bulk_create(order_items)  # Efficient bulk insert

            # Step 3: Calculate and update total amount
            order.total_amount = order.calculate_total_price()
            order.save(update_fields=['total_amount'])

            # Step 4: Clear the Cart
            cart_items.delete()
    def perform_create(self, serializer):
        user = self.request.user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            raise serializers.ValidationError({"error": "Your cart is empty!"})

        with transaction.atomic():
            order = serializer.save(user=user)
            order_items = [OrderItem(order=order, product=item.product, quantity=item.quantity) for item in cart_items]
            OrderItem.objects.bulk_create(order_items)  

            order.total_amount = order.calculate_total_price()
            order.save(update_fields=['total_amount'])

            cart_items.delete()


stripe.api_key = settings.STRIPE_SECRET_KEY  # Set in settings.py

class StripeCheckoutView(APIView):
    def post(self, request):
        try:
            order_id = request.data.get("order_id")
            payment_method = request.data.get("payment_method", "card")

            order = Order.objects.get(id=order_id)

            # Create a Stripe Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Convert to cents
                currency="usd",
                payment_method_types=["card"],
            )

            # Save payment details in DB
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_method,
                transaction_id=intent["id"],
                payment_status="pending",
            )

            return Response({
                "client_secret": intent["client_secret"],
                "payment_id": payment.id
            }, status=status.HTTP_201_CREATED)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        