from django import forms
from .models import Suggestion,Product

class SuggestionForm(forms.ModelForm):
    class Meta:
        model = Suggestion
        fields = '__all__'
        
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'      
