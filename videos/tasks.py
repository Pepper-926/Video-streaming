#modulo para gestionar las colas del cambio de formato de los videos
from celery import shared_task
import os, glob
from .utils import convertir_a_hls
from django.conf import settings
from .models import Videos

@shared_task
def convertir_video_a_hls(video_id, _unused_path):
    try:
        video = Videos.objects.get(id_video=video_id)

        # ----- conversión -----
        src_dir = os.path.join(settings.MEDIA_ROOT, 'videos', f'video{video_id}')
        src_mp4 = os.path.join(src_dir, 'original.mp4')
        out_dir = os.path.join(settings.MEDIA_ROOT, 'stream', str(video_id))
        print(f'Convirtiendo {src_mp4} a HLS en {out_dir}')
        convertir_a_hls(src_mp4, out_dir)

        # ----- marcar estado -----
        video.conversion_completa = True
        video.save(update_fields=['conversion_completa'])

        # ----- eliminar .mp4 restantes -----
        for mp4 in glob.glob(os.path.join(src_dir, '*.mp4')):
            try:
                os.remove(mp4)
            except FileNotFoundError:
                pass

        return f'Video {video_id} convertido y original eliminado'

    except Exception as e:
        print(f"[ERROR] Falló la conversión del video {video_id}: {e}. Se elimino el registro de la base de datos     ")
        video.delete()
        return f"[ERROR] Falló la conversión del video {video_id}"

