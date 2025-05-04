from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from user.models import Profile
from .models import Topluluklar
from django.core.files.base import ContentFile
import os
from django.conf import settings


@receiver(post_save, sender=Profile)
def create_or_update_topluluk(sender, instance, created, **kwargs):
    """
    Profile kaydedildiğinde, eğer role='community' ise otomatik olarak
    Topluluklar modeline kayıt ekler veya günceller
    """
    if instance.role == 'community' and instance.user:
        # Topluluk zaten var mı kontrol et
        topluluk, created = Topluluklar.objects.get_or_create(name=instance.user.username)
        
        # Profile'den topluluk bilgilerini güncelle
        if instance.img:
            topluluk.img = instance.img.name.split('/')[-1]  # Sadece dosya adını al
        
        # Description bilgisini güncelle eğer varsa
        if instance.description:
            topluluk.description = instance.description
            
        topluluk.save()


@receiver(post_delete, sender=Profile)
def delete_topluluk(sender, instance, **kwargs):
    """
    Profile silindiğinde, ona ait topluluğu da sil
    """
    if instance.role == 'community' and instance.user:
        try:
            topluluk = Topluluklar.objects.get(name=instance.user.username)
            topluluk.delete()
        except Topluluklar.DoesNotExist:
            pass  # Eğer topluluk zaten yoksa bir şey yapma


@receiver(post_save, sender=Topluluklar)
def update_profile_from_topluluk(sender, instance, **kwargs):
    """
    Topluluk güncellendiğinde, eğer ilişkili bir kullanıcı ve profil varsa
    profil bilgilerini günceller
    """
    try:
        # Topluluk adıyla eşleşen kullanıcıyı bul
        user = instance.get_user()
        if user and hasattr(user, 'profile') and user.profile.role == 'community':
            profile = user.profile
            
            # Topluluk resmi değiştiyse ve profil resmi farklıysa
            if instance.img:
                # Şu anki profil resmi farklı mı kontrol et
                current_img_name = os.path.basename(profile.get_image_path()) if profile.img else None
                if current_img_name != instance.img:
                    # Resmi static/img/ klasöründen al
                    img_path = os.path.join(settings.STATIC_ROOT, 'img', instance.img)
                    if os.path.exists(img_path):
                        # Profile modelinde resmi güncelle
                        with open(img_path, 'rb') as f:
                            content = ContentFile(f.read())
                            profile.img.save(instance.img, content, save=False)
            
            # Description güncelleme (opsiyonel)
            if instance.description and instance.description != profile.description:
                profile.description = instance.description
            
            # Profili kaydet (eğer değişiklik varsa)
            profile.save()
            
    except Exception as e:
        print(f"Profil güncellenirken hata oluştu: {e}") 