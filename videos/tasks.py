#modulo para gestionar las colas del cambio de formato de los videos
from celery import shared_task
import os, glob
from .utils import convertir_a_hls
from django.conf import settings
from .models import Videos

@shared_task
def convertir_video_a_hls(video_id, _unused_path):
    """
    • Convierte a HLS en MEDIA_ROOT/stream/<id>/
    • Marca conversion_completa = True
    • Borra original.mp4 (o cualquier .mp4) en MEDIA_ROOT/videos/video<id>/
    """
    video = Videos.objects.get(id_video=video_id)

    # ----- conversión -----
    src_dir   = os.path.join(settings.MEDIA_ROOT, 'videos', f'video{video_id}')
    src_mp4   = os.path.join(src_dir, 'original.mp4')
    out_dir   = os.path.join(settings.MEDIA_ROOT, 'stream', str(video_id))
    convertir_a_hls(src_mp4, out_dir)

    # ----- marcar estado -----
    video.conversion_completa = True
    video.save(update_fields=['conversion_completa'])

    # ----- eliminar todos los .mp4 restantes -----
    for mp4 in glob.glob(os.path.join(src_dir, '*.mp4')):
        try:
            os.remove(mp4)
        except FileNotFoundError:
            pass

    # (opcional) si ya no queda nada más y no quieres conservar miniatura:
    # if not os.listdir(src_dir):
    #     os.rmdir(src_dir)

    return f'Video {video_id} convertido y original eliminado'
