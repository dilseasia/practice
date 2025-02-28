from django.db import models


class Suggestion(models.Model):
    name = models.CharField(max_length=100)  # User's name
    email = models.EmailField()  # User's email
    message = models.TextField()  # Suggestion message
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"{self.name} - {self.email}"


class Product(models.Model):
    name = models.CharField(max_length=100)  # User's name
      
    description = models.TextField()  # Suggestion message
      # Timestamp

    def __str__(self):
        return f"{self.name} - {self.description}"