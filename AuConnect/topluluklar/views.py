from django.shortcuts import render
from django.http import HttpResponse
from .models import Topluluklar
from django.http import Http404  
from django.contrib import messages  
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')  # Giriş yapmamış kullanıcıları login sayfasına yönlendir
def liste(request):
    topluluklar = Topluluklar.objects.all()
    context = {
        "topluluklar" : topluluklar
    }
    return render(request, "topluluklar/list.html", context)
