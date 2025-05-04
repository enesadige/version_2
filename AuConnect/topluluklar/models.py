from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.templatetags.static import static

# Create your models here.

class Topluluklar(models.Model):
    name = models.CharField(max_length=100)
    img = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

    def get_image_path(self):
        return "/img/" + str(self.img)
    
    def get_user(self):
        """Topluluk adıyla eşleşen kullanıcıyı döndürür."""
        try:
            return User.objects.get(username=self.name)
        except User.DoesNotExist:
            return None

# Kategori modeli
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon name", null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ['name']
    
    def __str__(self):
        return self.name

# Gönderi modeli
class Post(models.Model):
    topluluk = models.ForeignKey(Topluluklar, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, verbose_name="Başlık")
    content = models.TextField(verbose_name="İçerik")
    image = models.CharField(max_length=100, null=True, blank=True, verbose_name="Resim")
    categories = models.ManyToManyField(Category, related_name='posts', verbose_name="Kategoriler")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Gönderi"
        verbose_name_plural = "Gönderiler"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_image_path(self):
        if self.image:
            return "/img/" + str(self.image)
        return None
    
    def get_categories_display(self):
        return ", ".join([category.name for category in self.categories.all()])
    