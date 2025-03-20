from django.shortcuts import render
from django.http import JsonResponse, HttpResponse

# Create your views here.
def login(request):
    return render(request, 'loginPage.html')

def signup(request):
    return render(request, 'signupPage.html')

def history(request):
    return render(request, 'historyPage.html')