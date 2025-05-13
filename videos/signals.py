from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Videos
from services.s3_storage import S3Manager

@receiver(post_delete, sender=Videos)
def eliminar_archivos_s3_video(sender, instance, **kwargs):
    try:
        s3 = S3Manager()
        s3.delete_folder(f'videos/video{instance.id_video}/')
    except Exception as e:
        print(f'Error eliminando carpeta S3 de video {instance.id_video}: {e}')