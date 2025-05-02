import os
import django

# Django ortamını ayarla
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuConnect.settings')
django.setup()

from django.utils.text import slugify
from topluluklar.models import Category

# Eski menüdeki kategoriler ve ikonları
categories_to_add = [
    {'name': 'Eğlence', 'icon': 'gamepad'},
    {'name': 'Akademik', 'icon': 'graduation-cap'},
    {'name': 'Kültür', 'icon': 'theater-masks'},
    {'name': 'Teknoloji', 'icon': 'laptop-code'},
    {'name': 'Sanat', 'icon': 'palette'},
    {'name': 'Spor', 'icon': 'running'},
]

for category_data in categories_to_add:
    # Eğer aynı isimde kategori yoksa oluştur
    name = category_data['name']
    icon = category_data['icon']
    slug = slugify(name)
    
    print(f"Kategori kontrol ediliyor: {name}")
    
    if not Category.objects.filter(name=name).exists():
        category = Category.objects.create(
            name=name,
            slug=slug,
            icon=icon,
            description=f"{name} kategorisine ait gönderiler"
        )
        print(f"Kategori oluşturuldu: {name} (ikon: {icon})")
    else:
        print(f"Kategori zaten mevcut: {name}")

print("\nİşlem tamamlandı. Toplam kategori sayısı:", Category.objects.count()) 