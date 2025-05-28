from django.urls import path    #bu url işini yapabilmek için eklememiz gerekiyo
from . import views             #views içindeki görüntüyü import edebilmek için

urlpatterns = [
    # Kullanıcı giriş sayfası
    path('login/', views.login, name = 'login'),
    
    # Kullanıcı kayıt sayfası
    path('register/', views.register, name = 'register'),
    
    # Kullanıcı çıkış işlemi
    path('logout/', views.logout, name = 'logout'),
    
    # Email doğrulama kodu gönderme
    path('send-verification-code/', views.send_verification_code, name='send_verification_code'),
    
    # Şifre sıfırlama kodu gönderme API endpoint'i
    path('api/send-password/', views.send_password_api, name='send_password_api'),
    
    # Şifre değiştirme API endpoint'i
    path('api/change-password/', views.change_password_api, name='change_password_api'),
]