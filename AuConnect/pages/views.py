from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request,"pages/index.html")

def about(request):
    return render(request,"pages/about.html")

@login_required(login_url='login')  # Giriş yapmamış kullanıcıları login sayfasına yönlendir
def anasayfa(request):
    """Ana sayfa görünümü - etkinlik ve duyurular gösterilir"""
    # Gönderi bilgilerini de ekle
    from topluluklar.models import Post, Category
    from topluluklar.views import get_or_create_profile
    from django.shortcuts import get_object_or_404
    
    profile = get_or_create_profile(request.user)
    
    # Kategori filtresi
    category_slug = request.GET.get('category', None)
    
    # Tüm gönderileri al
    all_posts = Post.objects.all().order_by('-created_at')  # En yeni gönderiler
    
    # Takip edilen topluluk gönderileri
    following_posts = []
    if profile.role == 'student':
        from topluluklar.models import Topluluklar
        following_topluluklar = Topluluklar.objects.filter(followers__user=request.user)
        following_posts = Post.objects.filter(topluluk__in=following_topluluklar).order_by('-created_at')
    
    # Kategori filtresi
    current_category = None
    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug)
            current_category = category_slug
            all_posts = all_posts.filter(categories=category)
            following_posts = following_posts.filter(categories=category)
        except Category.DoesNotExist:
            pass
    
    # Limit posts for display
    all_posts = all_posts[:10]  # En yeni 10 gönderi
    following_posts = following_posts[:10]  # En yeni 10 gönderi
    
    # Kategorileri al
    categories = Category.objects.all()
    
    context = {
        'all_posts': all_posts,
        'following_posts': following_posts,
        'categories': categories,
        'current_category': current_category,
    }
    
    return render(request, "pages/anasayfa.html", context)