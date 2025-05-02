from django.contrib import admin
from .models import Topluluklar, Category, Post

@admin.register(Topluluklar)
class TopluluklarAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'topluluk', 'get_categories_display', 'created_at')
    list_filter = ('topluluk', 'categories', 'created_at')
    search_fields = ('title', 'content', 'topluluk__name')
    filter_horizontal = ('categories',)
    date_hierarchy = 'created_at'
    
    def get_categories_display(self, obj):
        return obj.get_categories_display()
    get_categories_display.short_description = 'Kategoriler'
