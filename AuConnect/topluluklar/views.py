from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Topluluklar, Category, Post
from django.http import Http404  
from django.contrib import messages  
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.text import slugify
from profiles.models import Follow
from user.models import Profile
from django.core.exceptions import ObjectDoesNotExist
import json


def get_or_create_profile(user):
    """Kullanıcının profilini kontrol eder veya oluşturur"""
    try:
        return user.profile
    except ObjectDoesNotExist:
        profile = Profile(user=user, role='student')  # Varsayılan olarak öğrenci
        profile.save()
        return profile

@login_required(login_url='login')  # Giriş yapmamış kullanıcıları login sayfasına yönlendir
def liste(request):
    # URL'den arama terimini al
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
    
    context = {
        "topluluklar": topluluklar,
        "search_query": search_query
    }
    return render(request, "topluluklar/list.html", context)

def topluluk_detail(request, topluluk_id):
    """Topluluk detay sayfası"""
    topluluk = get_object_or_404(Topluluklar, id=topluluk_id)
    posts = Post.objects.filter(topluluk=topluluk).order_by('-created_at')
    
    # Kullanıcının takip durumunu kontrol et
    is_following = False
    if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.role == 'student':
        is_following = Follow.objects.filter(user=request.user, topluluk=topluluk).exists()
    
    # Eğer kullanıcı giriş yapmışsa takipçi sayısını göster
    followers_count = Follow.objects.filter(topluluk=topluluk).count()
    
    context = {
        'topluluk': topluluk,
        'posts': posts,
        'is_following': is_following,
        'followers_count': followers_count
    }
    return render(request, 'topluluklar/detail.html', context)

@login_required(login_url='login')
def create_post(request):
    """Gönderi oluşturma görünümü"""
    if request.method == 'POST':
        profile = get_or_create_profile(request.user)
        
        # Topluluk hesabı kontrolü
        if profile.role != 'community':
            messages.error(request, "Sadece topluluk hesapları gönderi oluşturabilir.")
            return redirect('anasayfa')
        
        # Formdaki verileri al
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.POST.get('image')
        category_ids = request.POST.getlist('categories')
        
        # Validasyon
        if not title or not content:
            messages.error(request, "Başlık ve içerik alanları zorunludur.")
            return redirect('profil')
            
        try:
            # Kullanıcının topluluğunu bul
            topluluk = Topluluklar.objects.get(name=request.user.username)
            
            # Gönderi oluştur
            post = Post.objects.create(
                topluluk=topluluk,
                title=title,
                content=content,
                image=image
            )
            
            # Kategorileri ekle
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

@login_required(login_url='login')
def edit_post(request, post_id):
    """Gönderi düzenleme görünümü"""
    post = get_object_or_404(Post, id=post_id)
    
    # Yetki kontrolü
    if post.topluluk.name != request.user.username:
        messages.error(request, "Bu gönderiyi düzenleme yetkiniz yok.")
        return redirect('anasayfa')
    
    if request.method == 'POST':
        # Formdaki verileri al
        title = request.POST.get('title')
        content = request.POST.get('content')
        image = request.POST.get('image')
        category_ids = request.POST.getlist('categories')
        
        # Validasyon
        if not title or not content:
            messages.error(request, "Başlık ve içerik alanları zorunludur.")
            return redirect('edit_post', post_id=post_id)
            
        # Gönderiyi güncelle
        post.title = title
        post.content = content
        if image:
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
    
    # GET isteği için kategorileri getir
    categories = Category.objects.all()
    selected_categories = post.categories.all().values_list('id', flat=True)
    
    context = {
        'post': post,
        'categories': categories,
        'selected_categories': list(selected_categories)
    }
    return render(request, 'topluluklar/edit_post.html', context)

@login_required(login_url='login')
def delete_post(request, post_id):
    """Gönderi silme görünümü"""
    post = get_object_or_404(Post, id=post_id)
    topluluk_id = post.topluluk.id  # Topluluk ID'sini al
    
    # Yetki kontrolü
    if post.topluluk.name != request.user.username:
        messages.error(request, "Bu gönderiyi silme yetkiniz yok.")
        return redirect('anasayfa')
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, "Gönderi başarıyla silindi!")
        return redirect('topluluk_detail', topluluk_id=topluluk_id)
        
    return render(request, 'topluluklar/delete_post.html', {'post': post})

@login_required(login_url='login')
def anasayfa_posts(request):
    """Ana sayfa gönderileri görünümü"""
    profile = get_or_create_profile(request.user)
    category_slug = request.GET.get('category', None)
    view_type = request.GET.get('view', 'all')  # all, following
    search_query = request.GET.get('search', '')  # Arama sorgusu
    
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

def post_api_detail(request, post_id):
    """Gönderi detaylarını JSON formatında döndüren API görünümü"""
    try:
        post = Post.objects.get(id=post_id)
        
        # Resim adlarını doğrudan döndür
        topluluk_image = None
        if post.topluluk.img:
            topluluk_image = post.topluluk.img
            
        post_image = None
        if post.image:
            post_image = post.image
            
        # Gönderi detaylarını oluştur
        data = {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'topluluk_id': post.topluluk.id,
            'topluluk_name': post.topluluk.name,
            'topluluk_image': topluluk_image,
            'image': post_image,
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
