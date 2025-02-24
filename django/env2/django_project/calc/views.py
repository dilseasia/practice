from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    return render(request, "index.html")


def add(request):
    value1 = int(request.GET["num1"])
    value2 = int(request.GET["num2"])
    res = value1 + value2

    return render(request, "results.html", {"results": res})
