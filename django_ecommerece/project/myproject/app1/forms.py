from django import forms
from .models import Suggestion,Employee

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = '__all__'
        

class EmployeeForm(forms.ModelForm):  # Make sure it inherits from ModelForm
    class Meta:
        model = Employee  # Link the form to the Employee model
        fields = ['name']  # Include only the 'name' field
