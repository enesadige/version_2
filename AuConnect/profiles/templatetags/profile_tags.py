from django import template
from user.models import Profile
from django.core.exceptions import ObjectDoesNotExist
from topluluklar.models import Topluluklar

register = template.Library()

@register.simple_tag
def get_profile(user):
    """Kullanıcının profilini güvenli bir şekilde alma"""
    try:
        return user.profile
    except ObjectDoesNotExist:
        # Eğer profil yoksa None döndür
        return None

@register.simple_tag
def get_profile_role(user):
    """Kullanıcının profil rolünü güvenli bir şekilde alma"""
    try:
        return user.profile.role
    except ObjectDoesNotExist:
        # Varsayılan olarak student döndür
        return 'student'

@register.simple_tag
def get_profile_image(user):
    """Kullanıcının profil resmini güvenli bir şekilde alma"""
    try:
        if user.profile.role == 'community':
            if user.profile.img:
                return user.profile.get_image_path()
            # Topluluk hesabı ama profil resmi yoksa
            return "/static/img/community-icon.jpg"
    except ObjectDoesNotExist:
        pass
    # Öğrenci hesabı veya profil bulunamadı ise
    return "/static/img/user-icon.jpg"

@register.simple_tag
def get_topluluk_image(user):
    """Topluluk hesabı için Topluluklar modelinden resim alma"""
    try:
        if user.profile.role == 'community':
            try:
                topluluk = Topluluklar.objects.get(name=user.username)
                if topluluk.img:
                    return topluluk.get_image_path()
            except Topluluklar.DoesNotExist:
                pass
    except ObjectDoesNotExist:
        pass
    # Resim bulunamadı ise None döndür, template varsayılan resmi kullanacak
    return None 