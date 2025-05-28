# Gerekli Django modüllerini içe aktar
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Topluluklar, Category, Post, ToplulukDegerlendirme
from django.http import Http404  
from django.contrib import messages  
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.text import slugify
from profiles.models import Follow
from user.models import Profile
from django.core.exceptions import ObjectDoesNotExist
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import models


# Kullanıcının profilini kontrol eder, yoksa varsayılan öğrenci rolüyle yeni profil oluşturur
def get_or_create_profile(user):
    try:
        return user.profile
    except ObjectDoesNotExist:
        # Profil yoksa varsayılan olarak öğrenci rolüyle yeni profil oluştur
        profile = Profile(user=user, role='student')  
        profile.save()
        return profile

# Topluluklar listesini gösterir, arama yapılabilir
@login_required(login_url='login')
def liste(request):
    search_query = request.GET.get('q', '')
    
    # Arama yapılmış mı kontrol et
    if search_query:
        # Topluluk adı veya açıklamasında arama yap
        topluluklar = Topluluklar.objects.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    else:
        # Tüm toplulukları getir
        topluluklar = Topluluklar.objects.all()
    
    # Template'e gönderilecek verileri hazırla
    context = {
        "topluluklar": topluluklar,
        "search_query": search_query
    }
    return render(request, "topluluklar/list.html", context)

# Topluluk detay sayfasını ve gönderilerini gösterir
@login_required(login_url='login')
def topluluk_detail(request, topluluk_id):
    """Topluluk detay sayfası görünümü"""
    # Topluluk bilgilerini getir
    topluluk = get_object_or_404(Topluluklar, id=topluluk_id)
    # Topluluğa ait gönderileri tarih sırasına göre getir
    posts = Post.objects.filter(topluluk=topluluk).order_by('-created_at')
    
    # Kullanıcının takip durumunu kontrol et
    is_following = False
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'student':
        is_following = Follow.objects.filter(user=request.user, topluluk=topluluk).exists()
    
    # Template'e gönderilecek verileri hazırla
    context = {
        'topluluk': topluluk,
        'posts': posts,
        'is_following': is_following
    }
    return render(request, 'topluluklar/detail.html', context)

# Topluluk hesapları için yeni gönderi oluşturma
@login_required(login_url='login')
def create_post(request):
    """Gönderi oluşturma görünümü"""
    if request.method == 'POST':
        # Kullanıcı profilini al veya oluştur
        profile = get_or_create_profile(request.user)
        
        # Topluluk hesabı kontrolü
        if profile.role != 'community':
            messages.error(request, "Sadece topluluk hesapları gönderi oluşturabilir.")
            return redirect('anasayfa')
        
        # Form verilerini al
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')  # Resim dosyasını al
        category_ids = request.POST.getlist('categories')
        
        # Form validasyonu
        if not title or not content:
            messages.error(request, "Başlık ve içerik alanları zorunludur.")
            return redirect('profil')
            
        try:
            # Kullanıcının topluluğunu bul
            topluluk = Topluluklar.objects.get(name=request.user.username)
            
            # Yeni gönderi oluştur
            post = Post.objects.create(
                topluluk=topluluk,
                title=title,
                content=content,
                image=image
            )
            
            # Seçilen kategorileri gönderiye ekle
            if category_ids:
                categories = Category.objects.filter(id__in=category_ids)
                post.categories.set(categories)
            
            messages.success(request, "Gönderi başarıyla oluşturuldu!")
            return redirect('topluluk_detail', topluluk_id=topluluk.id)
            
        except Topluluklar.DoesNotExist:
            messages.error(request, "Topluluk bulunamadı.")
            return redirect('profil')
    
    # GET isteği için kategorileri getir
    categories = Category.objects.all()
    return render(request, 'topluluklar/create_post.html', {'categories': categories})

# Gönderi düzenleme işlemlerini yönetir
@login_required(login_url='login')
def edit_post(request, post_id):
    """Gönderi düzenleme görünümü"""
    # Gönderiyi getir
    post = get_object_or_404(Post, id=post_id)
    
    # Yetki kontrolü
    if post.topluluk.name != request.user.username:
        messages.error(request, "Bu gönderiyi düzenleme yetkiniz yok.")
        return redirect('anasayfa')
    
    if request.method == 'POST':
        # Form verilerini al
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.FILES.get('image')
        category_ids = request.POST.getlist('categories')
        
        # Form validasyonu
        if not title or not content:
            messages.error(request, "Başlık ve içerik alanları zorunludur.")
            return redirect('edit_post', post_id=post_id)
            
        # Gönderiyi güncelle
        post.title = title
        post.content = content
        if image:  # Yeni resim yüklendiyse
            post.image = image
        post.save()
        
        # Kategorileri güncelle
        if category_ids:
            categories = Category.objects.filter(id__in=category_ids)
            post.categories.set(categories)
        else:
            post.categories.clear()
        
        messages.success(request, "Gönderi başarıyla güncellendi!")
        return redirect('topluluk_detail', topluluk_id=post.topluluk.id)
    
    # GET isteği için kategorileri ve seçili kategorileri getir
    categories = Category.objects.all()
    selected_categories = post.categories.all().values_list('id', flat=True)
    
    context = {
        'post': post,
        'categories': categories,
        'selected_categories': list(selected_categories)
    }
    return render(request, 'topluluklar/edit_post.html', context)

# Gönderi silme işlemlerini yönetir
@login_required(login_url='login')
def delete_post(request, post_id):
    """Gönderi silme görünümü"""
    # Gönderiyi getir
    post = get_object_or_404(Post, id=post_id)
    topluluk_id = post.topluluk.id
    
    # Yetki kontrolü
    if post.topluluk.name != request.user.username:
        messages.error(request, "Bu gönderiyi silme yetkiniz yok.")
        return redirect('anasayfa')
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Gönderi başarıyla silindi!")
        return redirect('topluluk_detail', topluluk_id=topluluk_id)
        
    return render(request, 'topluluklar/delete_post.html', {'post': post})

# Ana sayfada gönderileri filtreleme ve gösterme
@login_required(login_url='login')
def anasayfa_posts(request):
    """Ana sayfa gönderileri görünümü"""
    # Kullanıcı profilini al
    profile = get_or_create_profile(request.user)
    
    # Filtreleme parametrelerini al
    category_slug = request.GET.get('category', None)
    view_type = request.GET.get('view', 'all')  # all, following
    search_query = request.GET.get('search', '')
    
    # Kategori filtresi
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = Post.objects.filter(categories=category)
    else:
        posts = Post.objects.all()
    
    # Arama filtresi
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Takip filtrelemesi
    if view_type == 'following' and profile.role == 'student':
        # Kullanıcının takip ettiği toplulukları bul
        following_topluluklar = Topluluklar.objects.filter(
            followers__user=request.user
        )
        # Bu toplulukların gönderilerini filtrele
        posts = posts.filter(topluluk__in=following_topluluklar)
    
    # Kategorileri getir (sidebar için)
    categories = Category.objects.all()
    
    context = {
        'posts': posts.order_by('-created_at'),
        'categories': categories,
        'current_category': category_slug,
        'view_type': view_type,
        'search_query': search_query
    }
    
    return render(request, 'topluluklar/anasayfa_posts.html', context)

# Gönderi detaylarını JSON formatında döndüren API
@login_required(login_url='login')
def post_api_detail(request, post_id):
    """Gönderi detaylarını JSON formatında döndüren API görünümü"""
    try:
        post = Post.objects.get(id=post_id)
        
        # Gönderi detaylarını oluştur
        data = {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'topluluk_id': post.topluluk.id,
            'topluluk_name': post.topluluk.name,
            'topluluk_image': post.topluluk.get_image_path(),
            'image': post.image.url if post.image else None,
            'created_at': post.created_at.strftime('%d %b %Y, %H:%M'),
            'categories': [
                {
                    'id': category.id,
                    'name': category.name,
                    'icon': category.icon
                } for category in post.categories.all()
            ]
        }
        
        return JsonResponse(data)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Gönderi bulunamadı'}, status=404)

@login_required(login_url='login')
def topluluk_posts_api(request, topluluk_id):
    """Topluluk detaylarını ve gönderilerini JSON formatında döndüren API görünümü"""
    try:
        topluluk = Topluluklar.objects.get(id=topluluk_id)
        posts = Post.objects.filter(topluluk=topluluk).order_by('-created_at')[:5]  # Son 5 gönderi
        
        # Takipçi sayısını al
        follower_count = Follow.objects.filter(topluluk=topluluk).count()
        
        # Gönderi sayısını al
        post_count = Post.objects.filter(topluluk=topluluk).count()
        
        # Topluluk detaylarını oluştur
        data = {
            'id': topluluk.id,
            'name': topluluk.name,
            'description': topluluk.description,
            'image': topluluk.get_image_path(),
            'follower_count': follower_count,
            'post_count': post_count,
            'posts': [
                {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'image': post.image.url if post.image else None,
                    'created_at': post.created_at.strftime('%d %b %Y, %H:%M'),
                    'categories': [
                        {
                            'id': category.id,
                            'name': category.name,
                            'icon': category.icon
                        } for category in post.categories.all()
                    ]
                } for post in posts
            ]
        }
        
        return JsonResponse(data)
    except Topluluklar.DoesNotExist:
        return JsonResponse({'error': 'Topluluk bulunamadı'}, status=404)

@csrf_exempt
@login_required(login_url='login')
def topluluk_degerlendirme_api(request, topluluk_id):
    if request.method == 'POST':
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'student':
            return JsonResponse({'status': 'error', 'message': 'Sadece öğrenciler değerlendirme yapabilir.'}, status=403)
        try:
            topluluk = Topluluklar.objects.get(id=topluluk_id)
            data = json.loads(request.body)
            etkinlik_puani = int(data.get('etkinlik_puani', 0))
            aktiflik_puani = int(data.get('aktiflik_puani', 0))
            yonetim_puani = int(data.get('yonetim_puani', 0))
            vaat_puani = int(data.get('vaat_puani', 0))
            hakkaniyet_puani = int(data.get('hakkaniyet_puani', 0))
            degerlendirme, created = ToplulukDegerlendirme.objects.update_or_create(
                topluluk=topluluk,
                degerlendiren=request.user,
                defaults={
                    'etkinlik_puani': etkinlik_puani,
                    'aktiflik_puani': aktiflik_puani,
                    'yonetim_puani': yonetim_puani,
                    'vaat_puani': vaat_puani,
                    'hakkaniyet_puani': hakkaniyet_puani
                }
            )
            return JsonResponse({'status': 'success', 'message': 'Değerlendirme kaydedildi.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    elif request.method == 'GET':
        try:
            topluluk = Topluluklar.objects.get(id=topluluk_id)
            degerlendirmeler = ToplulukDegerlendirme.objects.filter(topluluk=topluluk)
            ortalama_puanlar = {
                'etkinlik_puani': degerlendirmeler.aggregate(models.Avg('etkinlik_puani'))['etkinlik_puani__avg'] or 0,
                'aktiflik_puani': degerlendirmeler.aggregate(models.Avg('aktiflik_puani'))['aktiflik_puani__avg'] or 0,
                'yonetim_puani': degerlendirmeler.aggregate(models.Avg('yonetim_puani'))['yonetim_puani__avg'] or 0,
                'vaat_puani': degerlendirmeler.aggregate(models.Avg('vaat_puani'))['vaat_puani__avg'] or 0,
                'hakkaniyet_puani': degerlendirmeler.aggregate(models.Avg('hakkaniyet_puani'))['hakkaniyet_puani__avg'] or 0
            }
            kullanici_degerlendirmesi = None
            if request.user.is_authenticated:
                try:
                    kullanici_degerlendirmesi = degerlendirmeler.get(degerlendiren=request.user)
                except ToplulukDegerlendirme.DoesNotExist:
                    pass
            return JsonResponse({
                'status': 'success',
                'data': {
                    'ortalama_puanlar': ortalama_puanlar,
                    'toplam_degerlendirme': degerlendirmeler.count(),
                    'kullanici_degerlendirmesi': {
                        'etkinlik_puani': kullanici_degerlendirmesi.etkinlik_puani if kullanici_degerlendirmesi else None,
                        'aktiflik_puani': kullanici_degerlendirmesi.aktiflik_puani if kullanici_degerlendirmesi else None,
                        'yonetim_puani': kullanici_degerlendirmesi.yonetim_puani if kullanici_degerlendirmesi else None,
                        'vaat_puani': kullanici_degerlendirmesi.vaat_puani if kullanici_degerlendirmesi else None,
                        'hakkaniyet_puani': kullanici_degerlendirmesi.hakkaniyet_puani if kullanici_degerlendirmesi else None,
                        'ortalama_puan': kullanici_degerlendirmesi.ortalama_puan if kullanici_degerlendirmesi else None
                    } if kullanici_degerlendirmesi else None
                }
            })
        except Topluluklar.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Topluluk bulunamadı.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'}, status=405)
