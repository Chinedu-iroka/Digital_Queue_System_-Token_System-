from django.apps import AppConfig


class TokenSystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Token_System'

    def ready(self):
        
        # signals
        import Token_System.signals
