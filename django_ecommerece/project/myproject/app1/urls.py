

from django.urls import path
from .views import submit_suggestion, view_suggestions,Home_View,Show

urlpatterns = [
    path('home/',Home_View,name="employee_name"),           
    path('submit/', submit_suggestion, name='submit_suggestion'),
    path('results/', view_suggestions, name='view_suggestions'),
    path('results1/',Show,name="show")
]
