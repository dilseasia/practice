from django.shortcuts import render,redirect,get_object_or_404
from .forms import SuggestionForm,ProductForm,ProductUpdateForm
from .models import Suggestion,Product
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth import login, logout
from django.contrib import messages

def home_view(request):
    return render (request,"home.html")

def suggestion_Get(request):
  if request.method =="POST":
    form = SuggestionForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect ("thanks")
    
  else:
      form=SuggestionForm()
      return render(request ,"suggestion.html" , {"form":form})
  

  
def Thanks_View(request):    
      return render(request,"thanks.html")
  
def Sug_View(request):
    sug=Suggestion.objects.all()
    return render(request,"results.html",{'suggestion':sug})


def Product_Get(request):
  if request.method =="POST":
    form = ProductForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect ("products_output")
  else:
      form=ProductForm()
      return render(request ,"products.html" , {"form":form})
  
def Product_View(request):
    pro=Product.objects.all()
    return render (request,"products_output.html",{"products":pro})
   


def update_product(request, id):
    product = get_object_or_404(Product, id=id)  
    if request.method == "POST":
        form = ProductUpdateForm(request.POST, instance=product) 
        if form.is_valid():
            form.save()
            return redirect("products_output")
    else:
        form = ProductUpdateForm(instance=product)  

    return render(request, "update_product.html", {"form": form})


def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect("products_output")

def Product_View_User(request):
    prod=Product.objects.all()
    return render (request,"product_list_user.html",{"products_list":prod})


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)  # Authenticate user
        if form.is_valid():
            user = form.get_user()  # Get authenticated user
            login(request, user)  # Log in the user
            messages.success(request, f"Welcome {user.username}!")  # Show welcome message
            return redirect('/')  # Redirect to task management page
    else:
        form = AuthenticationForm()  
    return render(request, 'login.html', {'form': form})  
 
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

def About(request):
    return render(request,"about.html")

def Dummy(request):
    return render (request,"dummy.html")