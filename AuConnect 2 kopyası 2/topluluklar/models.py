from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.templatetags.static import static

class Topluluklar(models.Model):
    name = models.CharField(max_length=100)
    img = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.name
    def get_image_path(self):
        return "/img/" + str(self.img)
    
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
    image = models.ImageField(upload_to='post_images/', null=True, blank=True, verbose_name="Resim")
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
            return self.image.url
        return None    
    def get_categories_display(self):
        return ", ".join([category.name for category in self.categories.all()])
    
class ToplulukDegerlendirme(models.Model):
    topluluk = models.ForeignKey(Topluluklar, on_delete=models.CASCADE, related_name='degerlendirmeler')
    degerlendiren = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topluluk_degerlendirmeleri')
    etkinlik_puani = models.IntegerField(default=0)
    aktiflik_puani = models.IntegerField(default=0)
    yonetim_puani = models.IntegerField(default=0)
    vaat_puani = models.IntegerField(default=0)
    hakkaniyet_puani = models.IntegerField(default=0)
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleme_tarihi = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Topluluk Değerlendirmesi"
        verbose_name_plural = "Topluluk Değerlendirmeleri"
        unique_together = ['topluluk', 'degerlendiren']
    def __str__(self):
        return f"{self.topluluk.name} - {self.degerlendiren.username} Değerlendirmesi"
    @property
    def ortalama_puan(self):
        return (self.etkinlik_puani + self.aktiflik_puani + self.yonetim_puani + self.vaat_puani + self.hakkaniyet_puani) / 5
    
