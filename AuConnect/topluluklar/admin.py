from django.contrib import admin
from .models import Topluluklar

class ToplulukAdmin(admin.ModelAdmin):

    list_display = ("id","name")

admin.site.register(Topluluklar,ToplulukAdmin)
