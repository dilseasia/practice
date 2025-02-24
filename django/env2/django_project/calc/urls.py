from django.urls import path
from . import views  # Import views from the same directory

urlpatterns = [
    path("", views.home, name="home"),
    path("add", views.add, name="add"),  # Define at least one route
]
