from django.apps import AppConfig


class TopluluklarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'topluluklar'
    
    def ready(self):
        import topluluklar.signals  # signals'ı import et

