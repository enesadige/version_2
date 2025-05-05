from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Kullanıcı oluşturulduğunda profil oluştur veya güncelle"""
    if created:
        # Eğer kullanıcının mail adresiyle ilişkili geçici bir profil varsa, o profili kullan
        temp_profile = Profile.objects.filter(temporary_email=instance.email, user__isnull=True).first()
        
        if temp_profile:
            # Geçici profili kullanıcıya bağla
            temp_profile.user = instance
            temp_profile.save()
        else:
            # Geçici profil yoksa yeni oluştur
            Profile.objects.create(user=instance)

@receiver(pre_save, sender=Profile)
def update_profile(sender, instance, **kwargs):
    """Profil kaydedilmeden önce tutarlılık kontrollerini yap"""
    # Eğer profilin bir kullanıcısı varsa, geçici email ve kullanıcı email'i tutarlı olsun
    if instance.user and instance.temporary_email:
        if instance.user.email != instance.temporary_email:
            instance.temporary_email = None  # Artık geçici email'e gerek yok
