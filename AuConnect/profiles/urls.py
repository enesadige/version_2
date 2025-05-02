from django.urls import path
from . import views

urlpatterns = [
    path("", views.profile_redirect, name="profile"),  # Ana profil URL'i, kullanıcı tipine göre yönlendirir
    path("profil/", views.profil, name="profil"),  # Topluluk profili 
    path("profilOgrenci/", views.profilOgrenci, name="profilOgrenci"),  # Öğrenci profili
    
    # Takip API'leri
    path("api/toggle-follow/", views.toggle_follow, name="toggle_follow"),
    path("api/check-follow/<int:topluluk_id>/", views.check_follow, name="check_follow"),
]