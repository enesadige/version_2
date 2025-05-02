from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile
from django.utils.html import format_html

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('display_username', 'display_email', 'role', 'email_verified')
    list_filter = ('role', 'email_verified')
    search_fields = ('user__username', 'user__email', 'temporary_email')
    readonly_fields = ('verification_code',)
    
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user', 'role', 'email_verified')
        }),
        ('Doğrulama Bilgileri', {
            'fields': ('temporary_email', 'verification_code')
        }),
    )
    
    def display_username(self, obj):
        if obj.user:
            return obj.user.username
        return format_html('<span style="color: #999;">Geçici Kullanıcı</span>')
    display_username.short_description = 'Kullanıcı Adı'
    
    def display_email(self, obj):
        if obj.user:
            return obj.user.email
        return obj.temporary_email
    display_email.short_description = 'E-posta'
    
    def save_model(self, request, obj, form, change):
        """Profil kaydedilirken kullanıcı atama işlemini düzelt"""
        if 'user' in form.changed_data and obj.user:
            # Kullanıcı değiştiyse geçici email'i sil
            obj.temporary_email = None
        super().save_model(request, obj, form, change)

admin.site.register(Profile, ProfileAdmin)
