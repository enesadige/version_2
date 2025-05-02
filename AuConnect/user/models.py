from django.db import models
from django.contrib.auth.models import User
import uuid


class Profile(models.Model):
    USER_ROLES = (
        ('student', 'Öğrenci'),
        ('community', 'Topluluk'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Kullanıcı")
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student', verbose_name="Rol")
    email_verified = models.BooleanField(default=False, verbose_name="Email Doğrulandı")
    verification_code = models.UUIDField(default=uuid.uuid4, verbose_name="Doğrulama Kodu")
    temporary_email = models.EmailField(null=True, blank=True, verbose_name="Geçici Email")

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.get_role_display()}"
        return f"Geçici Profil - {self.temporary_email}"
    
    def save(self, *args, **kwargs):
        # Kullanıcı varsa ve geçici email adresi hala kayıtlıysa, temizle
        if self.user and self.temporary_email:
            if self.user.email != self.temporary_email:
                self.temporary_email = None
        super().save(*args, **kwargs)
        
    class Meta:
        verbose_name = "Kullanıcı Profili"
        verbose_name_plural = "Kullanıcı Profilleri"