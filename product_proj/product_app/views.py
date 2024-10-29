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
def category(request):
    return render(request, 'category.html')
def seller(request):
    return render(request, 'seller.html')
def branch(request):
    return render(request, 'branch.html')
def settings(request):
    return render(request, 'settings.html')
def report(request):
    return render(request, 'report.html')