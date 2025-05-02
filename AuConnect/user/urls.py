from django.urls import path    #bu url işini yapabilmek için eklememiz gerekiyo
from . import views             #views içindeki görüntüyü import edebilmek için

urlpatterns = [
    path('login/', views.login, name = 'login'),
    path('register/', views.register, name = 'register'),
    path('logout/', views.logout, name = 'logout'),
    path('send-verification-code/', views.send_verification_code, name='send_verification_code'),
]