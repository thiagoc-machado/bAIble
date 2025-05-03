from django.apps import AppConfig

class BibliaContextoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'biblia_contexto'

    def ready(self):
        from .memory_cleaner import start_memory_cleaner
        start_memory_cleaner()
