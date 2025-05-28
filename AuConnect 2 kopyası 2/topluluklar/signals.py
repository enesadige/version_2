from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from user.models import Profile
from .models import Topluluklar

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


