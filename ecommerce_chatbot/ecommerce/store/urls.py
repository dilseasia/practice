from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, ProfileView, 
    CategoryViewSet, BrandViewSet, ProductViewSet,
    CartViewSet, OrderViewSet, StripeCheckoutView
)

# ✅ Use DefaultRouter for ViewSets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    # 🔹 Authentication Endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("payments/checkout/", StripeCheckoutView.as_view(), name="stripe-checkout"),
    
    # 🔹 Include the router URLs
    path('', include(router.urls)),  # All the viewset URLs
    
    # If you want to handle PATCH on specific orders
    path('orders/<int:pk>/', OrderViewSet.as_view({'patch': 'partial_update'}), name='order-partial-update'),
]
