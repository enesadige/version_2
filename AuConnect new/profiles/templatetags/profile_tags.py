from django import template
from user.models import Profile
from django.core.exceptions import ObjectDoesNotExist

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
        if user.profile.role == 'community' and user.profile.img:
            return user.profile.get_image_path()
    except ObjectDoesNotExist:
        pass
    # Varsayılan resim döndür
    return None 