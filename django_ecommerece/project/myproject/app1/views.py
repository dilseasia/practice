from django.shortcuts import render, redirect
from .forms import SuggestionForm,EmployeeForm
from .models import Suggestion,Employee


def submit_suggestion(request):
    if request.method == 'POST':
        form = SuggestionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('results')  # Redirect after successful submission
    else:
        form = SuggestionForm()
    return render(request, 'suggestion_form.html', {'form': form})



def view_suggestions(request):
    suggestions = Suggestion.objects.all()
    return render(request, 'results.html', {'suggestions': suggestions})



def EmployeeName(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)  # Use the correct form name
        if form.is_valid():  # Fix is_Valid() to is_valid()
            form.save()
            return redirect('suggestion_form')  # Redirect to the next page
    else:
        form = EmployeeForm()  # Use the correct form name
    return render(request, "home.html", {'form': form})  # Fix "hml" to "html"

def Show(request):
    get=Employee.objects.all()
    return render (request,"results1.html",{'ge':get})