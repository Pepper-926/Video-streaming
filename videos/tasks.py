#modulo para gestionar las colas del cambio de formato de los videos
from celery import shared_task
import os
from .utils import convertir_a_hls
from django.conf import settings
from .models import Videos

@shared_task
def convertir_video_a_hls(video_id, video_path):
    video = Videos.objects.get(id_video=video_id)

    output_dir = os.path.join(settings.MEDIA_ROOT, 'stream', str(video_id))
    convertir_a_hls(video_path, output_dir)
    video.conversion_completa = True
    video.save()
    
    return f"Conversión completada para video {video_id}"