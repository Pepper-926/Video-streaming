from django.apps import AppConfig


class VideosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'videos'

class VideosConfig(AppConfig):
    name = 'videos'

    def ready(self):
        import videos.signals  # conecta las señales
