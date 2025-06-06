from django.db import models
from django.contrib.auth.models import User
import uuid


class Profile(models.Model):
    """
    Kullanıcı profili modeli. Hem öğrenciler hem de topluluklar için kullanılır.
    Kullanıcı bilgilerini ve topluluk özelliklerini içerir.
    """
    USER_ROLES = (
        ('student', 'Öğrenci'),
        ('community', 'Topluluk'),
    )
    # Temel kullanıcı bilgileri
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Kullanıcı")
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student', verbose_name="Rol")
    email_verified = models.BooleanField(default=False, verbose_name="Email Doğrulandı")
    verification_code = models.UUIDField(default=uuid.uuid4, verbose_name="Doğrulama Kodu")
    temporary_email = models.EmailField(null=True, blank=True, verbose_name="Geçici Email")
    
    # Topluluklar için eklenen alanlar
    img = models.ImageField(upload_to='profile_images/', null=True, blank=True, verbose_name="Profil Resmi")
    description = models.TextField(null=True, blank=True, verbose_name="Açıklama")
    members_count = models.PositiveIntegerField(default=0, verbose_name="Üye Sayısı")
    founded_date = models.DateField(null=True, blank=True, verbose_name="Kuruluş Tarihi")
    website = models.URLField(null=True, blank=True, verbose_name="Web Sitesi")
    social_media = models.JSONField(null=True, blank=True, verbose_name="Sosyal Medya Hesapları")

    def __str__(self):
        """
        Profil nesnesinin string temsilini döndürür.
        Kullanıcı varsa kullanıcı adı ve rolü, yoksa geçici email adresini gösterir.
        """
        if self.user:
            return f"{self.user.username} - {self.get_role_display()}"
        return f"Geçici Profil - {self.temporary_email}"
    
    def save(self, *args, **kwargs):
        """
        Profil kaydedilirken çalışır.
        Kullanıcı varsa ve geçici email adresi hala kayıtlıysa, temizler.
        """
        if self.user and self.temporary_email:
            if self.user.email != self.temporary_email:
                self.temporary_email = None
        super().save(*args, **kwargs)
    
    def get_image_path(self):
        """
        Profil resminin URL'sini döndürür.
        Resim yoksa varsayılan resim yolunu döndürür.
        """
        if self.img:
            return self.img.url
        return "/static/img/user-ico.png"
        
    class Meta:
        """
        Model meta bilgileri.
        Admin panelinde görünecek isimleri belirler.
        """
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"



        