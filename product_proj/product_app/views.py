from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')
def signin(request):
    return render(request, 'signin.html')
def register(request):
    return render(request, 'register.html')
def products(request):
    return render(request, 'products.html')