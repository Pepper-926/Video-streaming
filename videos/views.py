import os  # Para trabajar con paths y nombres de archivos
import shutil  # Para eliminar directorios completos
from django.conf import settings  # Para obtener el MEDIA_PATH
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from .decoradores import verificar_token
from .forms import VideoUploadForm  # Obtener form que se devuelve al cliente
from .models import Videos, EtiquetasDeVideos
from .querys import asociar_etiquetas
from .tasks import convertir_video_a_hls
from .utils import generar_urls_firmadas_para_stream, optimizar_imagen
from usuarios.models import Canales
from django.views.decorators.csrf import csrf_exempt #para pruebas

def index(request):
    return render(request, 'inicio.html')

@verificar_token
def form_video(request):
    form = VideoUploadForm()
    return render(request, 'video.html', {'form': form})

#Vista de /videos
@method_decorator(verificar_token, name='post')
class VideosView(View):
    def get(self, request):
        videos = Videos.objects.filter(publico=True)
        data = [{
            'id_video': v.id_video,
            'titulo': v.titulo,
            'descripcion': v.descripcion,
            'link': v.link,
            'miniatura': v.miniatura,
            'etiquetas': [
                etiqueta.categoria
                for etiqueta in EtiquetasDeVideos.objects.filter(id_video=v.id_video)
            ]
        } for v in videos]
        return JsonResponse({'videos': data}, status=200)
    
    @transaction.atomic
    def post(self, request):
        form = VideoUploadForm(request.POST, request.FILES)
        if not form.is_valid():
            return redirect('/videos/upload')

        # 1 ─── Guardar video en rutas TEMPORALES ─────────────────────────
        video_file     = form.cleaned_data['file']
        tmp_video_name = video_file.name
        tmp_video_path = os.path.join(settings.MEDIA_ROOT, 'tmp', tmp_video_name)

        os.makedirs(os.path.dirname(tmp_video_path), exist_ok=True)
        with open(tmp_video_path, 'wb+') as dest:
            for chunk in video_file.chunks():
                dest.write(chunk)

        thumbnail = form.cleaned_data.get('thumbnail')

        # 2 ─── Crear registro con link vacío para obtener id ──────────────
        canal = Canales.objects.get(id_usuario=request.usuario)
        es_publico  = form.cleaned_data['visibility'] == 'public'

        video = Videos.objects.create(
            link      = '',
            miniatura = '',
            titulo    = form.cleaned_data['title'],
            descripcion = form.cleaned_data['description'],
            publico   = es_publico,
            id_canal  = canal
        )

        # 3 ─── Construir rutas DEFINITIVAS usando id_video ────────────────
        vid_dir = f"videos/video{video.id_video}"
        os.makedirs(os.path.join(settings.MEDIA_ROOT, vid_dir), exist_ok=True)

        final_video_rel = f"{vid_dir}/index.m3u8"
        final_video_fs  = os.path.join(settings.MEDIA_ROOT, final_video_rel)

        # mueve el mp4 temporal al lugar donde FFmpeg lo leerá
        final_src_mp4    = f"{vid_dir}/original.mp4"
        final_src_mp4_fs = os.path.join(settings.MEDIA_ROOT, final_src_mp4)
        os.rename(tmp_video_path, final_src_mp4_fs)

        # 4 ─── Procesar miniatura (si se subió) ───────────────────────────
        final_thumb_rel = None
        if thumbnail:
            final_thumb_rel = f"{vid_dir}/miniatura.jpg"    # <-- esta ruta relativa es para la base de datos

            # Primero guardamos en videos/video{id}/miniatura.jpg
            final_thumb_fs = os.path.join(settings.MEDIA_ROOT, final_thumb_rel)
            miniatura_base64 = optimizar_imagen(thumbnail)

            from base64 import b64decode
            with open(final_thumb_fs, 'wb') as f:
                f.write(b64decode(miniatura_base64))

            # Luego copiamos también a stream/{id}/miniatura.jpg
            final_thumb_stream_fs = os.path.join(settings.MEDIA_ROOT, 'stream', str(video.id_video), 'miniatura.jpg')
            os.makedirs(os.path.dirname(final_thumb_stream_fs), exist_ok=True)

            # Copia desde videos/video{id}/miniatura.jpg hacia stream/{id}/miniatura.jpg
            shutil.copyfile(final_thumb_fs, final_thumb_stream_fs)

        # 5 ─── Actualizar registro y lanzar Celery ───────────────────────
        video.link      = final_video_rel
        video.miniatura = final_thumb_rel
        video.save(update_fields=['link', 'miniatura'])

        convertir_video_a_hls.delay(video.id_video, final_src_mp4_fs)

        # etiquetas
        asociar_etiquetas(video, form.cleaned_data['tags'])

        return redirect(f'/videos/subida/{video.id_video}')

#Vista que devuelve si el video ya esta listo para subirse
@verificar_token
def video_estado(request, video_id):
    try:
        video = Videos.objects.get(id_video=video_id)  # usa id_video si así es tu PK
        return JsonResponse({'conversion_completa': video.conversion_completa}, status=200)
    except Videos.DoesNotExist:
        return JsonResponse({'conversion_completa': False}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

#vista que genera los urls firmados para que el cliente suba el video
@verificar_token
@require_GET
def obtener_urls_s3(request, video_id):
    try:
        urls = generar_urls_firmadas_para_stream(video_id)
        return JsonResponse({'archivos': urls})
    except FileNotFoundError:
        return JsonResponse({'error': 'Video aún no procesado o no existe'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
#View donde el usuario sube el video.
@verificar_token
def confirmar_subida(request, video_id):
    return render(request, 'video_subida.html', {'video_id': video_id})

@verificar_token
@require_POST
def video_nube(request, video_id):
    """
    Frontend avisa que todos los fragmentos ya están en S3:
    • marca estado=True (listo para revisión)
    • elimina la carpeta local media/stream/<id_video>/
    """
    try:
        video = Videos.objects.get(id_video=video_id)
        video.estado = True
        video.save(update_fields=['estado'])

        #Eliminamos archivos temporales.
        dir_to_delete = os.path.join(settings.MEDIA_ROOT, 'stream', str(video_id))
        shutil.rmtree(dir_to_delete, ignore_errors=True)   # borra todo el árbol
        dir_to_delete = os.path.join(settings.MEDIA_ROOT, 'videos', f'video{video_id}')
        shutil.rmtree(dir_to_delete, ignore_errors=True) 

        return JsonResponse({'ok': True})
    except Videos.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Video no existe'}, status=404)