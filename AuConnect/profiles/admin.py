from django.contrib import admin
from .models import Follow

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'topluluk', 'date_followed')
    list_filter = ('date_followed',)
    search_fields = ('user__username', 'topluluk__name')
    date_hierarchy = 'date_followed'
