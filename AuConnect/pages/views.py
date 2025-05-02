from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request,"pages/index.html")

def about(request):
    return render(request,"pages/about.html")

@login_required(login_url='login')  # Giriş yapmamış kullanıcıları login sayfasına yönlendir
def anasayfa(request):
    return render(request, "pages/anasayfa.html")