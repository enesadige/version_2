from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from user.models import Profile
from django.core.exceptions import ObjectDoesNotExist
from .models import Follow
from topluluklar.models import Topluluklar, Post
from django.views.decorators.http import require_POST
import json

# Profil kontrolü ve oluşturma fonksiyonu
def get_or_create_profile(user):
    try:
        # Profil varsa onu döndür
        return user.profile
    except ObjectDoesNotExist:
        # Profil yoksa yeni bir tane oluştur
        profile = Profile(user=user, role='student')  # Varsayılan olarak öğrenci
        profile.save()
        return profile

@login_required(login_url='login')
def profil(request):
    # Profilin olup olmadığını kontrol et, yoksa oluştur
    profile = get_or_create_profile(request.user)
    
    # Eğer kullanıcı topluluk değilse, öğrenci profiline yönlendir
    if profile.role != 'community':
        return redirect('profilOgrenci')
    
    # Topluluğun takipçilerini al
    followers_count = Follow.objects.filter(topluluk__name=request.user.username).count()
    
    # Kullanıcının topluluğunu bul
    try:
        topluluk = Topluluklar.objects.get(name=request.user.username)
    except Topluluklar.DoesNotExist:
        topluluk = None
    
    # Topluluk profili için gerekli verileri hazırla
    context = {
        'profile': profile,
        'followers_count': followers_count,
        'topluluk': topluluk
    }
    return render(request, "Profile/profil.html", context)

@login_required(login_url='login')
def profilOgrenci(request):
    # Profilin olup olmadığını kontrol et, yoksa oluştur
    profile = get_or_create_profile(request.user)
    
    # Eğer kullanıcı öğrenci değilse, topluluk profiline yönlendir
    if profile.role == 'community':
        return redirect('profil')
    
    # Öğrencinin takip ettiği toplulukları al
    following = Follow.objects.filter(user=request.user).select_related('topluluk')
    
    # Öğrenci profili için gerekli verileri hazırla
    context = {
        'profile': profile,
        'following': following
    }
    return render(request, "Profile/profilOgrenci.html", context)

# Genel profil sayfası - kullanıcı tipine göre yönlendirme yapar
@login_required(login_url='login')
def profile_redirect(request):
    # Profilin olup olmadığını kontrol et, yoksa oluştur
    profile = get_or_create_profile(request.user)
    
    if profile.role == 'community':
        return redirect('profil')
    else:
        return redirect('profilOgrenci')

# Topluluk takip etme/bırakma API'si
@login_required(login_url='login')
@require_POST
def toggle_follow(request):
    # AJAX isteği veya form data olarak verilerini al
    topluluk_id = request.POST.get('topluluk_id')
    action = request.POST.get('action')
    
    if not topluluk_id:
        return JsonResponse({'status': 'error', 'message': 'Topluluk ID\'si gereklidir.'}, status=400)
    
    # Kullanıcı topluluk mu kontrol et
    profile = get_or_create_profile(request.user)
    if profile.role == 'community':
        return JsonResponse({'status': 'error', 'message': 'Topluluklar diğer toplulukları takip edemez.'}, status=400)
    
    # Topluluğu bul
    try:
        topluluk = Topluluklar.objects.get(id=topluluk_id)
    except Topluluklar.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Topluluk bulunamadı.'}, status=404)
    
    # Takip/bırakma aksiyonu
    follow_exists = Follow.objects.filter(user=request.user, topluluk=topluluk).exists()
    
    if action == 'follow' and not follow_exists:
        # Takip et
        Follow.objects.create(user=request.user, topluluk=topluluk)
        return JsonResponse({
            'status': 'success', 
            'following': True,
            'message': f'{topluluk.name} topluluğunu takip etmeye başladınız.'
        })
    elif action == 'unfollow' and follow_exists:
        # Takibi bırak
        Follow.objects.filter(user=request.user, topluluk=topluluk).delete()
        return JsonResponse({
            'status': 'success', 
            'following': False,
            'message': f'{topluluk.name} topluluğunu takipten çıktınız.'
        })
    elif not action:
        # action belirtilmemişse, toggle olarak davran
        if follow_exists:
            Follow.objects.filter(user=request.user, topluluk=topluluk).delete()
            return JsonResponse({
                'status': 'success', 
                'following': False,
                'message': f'{topluluk.name} topluluğunu takipten çıktınız.'
            })
        else:
            Follow.objects.create(user=request.user, topluluk=topluluk)
            return JsonResponse({
                'status': 'success', 
                'following': True,
                'message': f'{topluluk.name} topluluğunu takip etmeye başladınız.'
            })
    
    return JsonResponse({
        'status': 'success', 
        'following': follow_exists,
        'message': 'İşlem başarılı.'
    })

# Takip durumunu kontrol etme API'si
@login_required(login_url='login')
def check_follow(request, topluluk_id):
    # Kullanıcı topluluk mu kontrol et
    profile = get_or_create_profile(request.user)
    if profile.role == 'community':
        return JsonResponse({'following': False})
    
    # Takip durumunu kontrol et
    is_following = Follow.objects.filter(user=request.user, topluluk_id=topluluk_id).exists()
    
    return JsonResponse({'following': is_following})

