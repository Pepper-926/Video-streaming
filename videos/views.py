import os #Para trabajar con paths y nombres de archivos
from django.shortcuts import render, redirect
from .models import Videos, VideosEtiquetas, Etiquetas
from canales.models import Canales
from .forms import VideoUploadForm #Obtener form que se devuelve al cliente
from django.conf import settings #Para obtener el MEDIA_PATH
from .querys import asociar_etiquetas
from .tasks import convertir_video_a_hls
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from .utils import generar_urls_firmadas_para_stream

from django.views.decorators.csrf import csrf_exempt #para pruebas

def index(request):
    return render(request, 'inicio.html')

def form_video(request):
    form = VideoUploadForm()
    return render(request, 'video.html', {'form': form})

def subir_video(request):
    """
    1. Recibe el formulario con archivo de video, miniatura y metadatos.
    2. Guarda los archivos en MEDIA_ROOT/videos/  y MEDIA_ROOT/imagenes/
    3. Crea el registro en la BD (incluye 'publico' según visibilidad elegida).
    4. Lanza la tarea Celery para convertir a HLS.
    5. Redirige a /videos/subida/<id>  para la fase de subida a S3.
    """
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():

            # ---------- 1.  VIDEO ----------
            video_file     = form.cleaned_data['file']
            video_filename = video_file.name
            video_path_db  = os.path.join('videos', video_filename)  # se guarda en la BD
            video_path_fs  = os.path.join(settings.MEDIA_ROOT, video_path_db)

            with open(video_path_fs, 'wb+') as dest:
                for chunk in video_file.chunks():
                    dest.write(chunk)

            # ---------- 2.  MINIATURA (opcional) ----------
            thumbnail      = form.cleaned_data.get('thumbnail')
            thumbnail_path_db = None
            if thumbnail:
                thumb_filename   = thumbnail.name
                thumbnail_path_db = os.path.join('imagenes', thumb_filename)
                thumb_path_fs    = os.path.join(settings.MEDIA_ROOT, thumbnail_path_db)
                with open(thumb_path_fs, 'wb+') as dest:
                    for chunk in thumbnail.chunks():
                        dest.write(chunk)

            # ---------- 3.  VISIBILIDAD ----------
            es_publico = form.cleaned_data['visibility'] == 'public'

            # ---------- 4.  CREAR REGISTRO ----------
            # (Temporal) canal fijo hasta tener autenticación
            canal = Canales.objects.get(id_canal=1)

            video = Videos.objects.create(
                link        = video_path_db,                  # ruta relativa
                titulo      = form.cleaned_data['title'],
                descripcion = form.cleaned_data['description'],
                miniatura   = thumbnail_path_db,
                publico     = es_publico,
                id_canal    = canal
            )

            # ---------- 5.  CONVERTIR A HLS EN SEGUNDO PLANO ----------
            convertir_video_a_hls.delay(video.id_video, video_path_fs)

            # ---------- 6.  ETIQUETAS ----------
            asociar_etiquetas(video, form.cleaned_data['tags'])

            # ---------- 7.  REDIRECCIÓN A PÁGINA DE SUBIDA ----------
            return redirect(f'/videos/subida/{video.id_video}')

    # Si no es POST o el form no es válido, vuelve al formulario
    return redirect('/videos/upload')

#Vista que devuelve si el video ya esta listo para subirse
def video_estado(request, video_id):
    if False:#not request.user.is_authenticated:  Esto hay que quitarlo una vez que ya se puedan manejar sesiones
        return redirect('/registrar')
    
    try:
        video = Videos.objects.get(id_video=video_id)  # usa id_video si así es tu PK
        return JsonResponse({'conversion_completa': video.conversion_completa}, status=200)
    except Videos.DoesNotExist:
        return JsonResponse({'conversion_completa': False}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

#vista que genera los urls firmados para que el cliente suba el video 
@csrf_exempt
@require_GET
def obtener_urls_s3(request, video_id): 
    if False:#not request.user.is_authenticated:  Esto hay que quitarlo una vez que ya se puedan manejar sesiones
        return JsonResponse({'error': 'No autorizado'}, status=403)

    try:
        urls = generar_urls_firmadas_para_stream(video_id)
        return JsonResponse({'archivos': urls})
    except FileNotFoundError:
        return JsonResponse({'error': 'Video aún no procesado o no existe'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
#View donde el usuario sube el video.
def confirmar_subida(request, video_id):
    if False:#not request.user.is_authenticated:
        return redirect('/registrar')

    return render(request, 'video_subida.html', {'video_id': video_id})


@require_POST
def video_nube(request, video_id):
    """
    Marca el vídeo como ‘subido a la nube’ (estado=True) cuando
    el frontend acaba de transferir todos los fragmentos a S3.
    """
    try:
        video = Videos.objects.get(id_video=video_id)
        video.estado = True          # listo para revisión del admin
        video.save(update_fields=['estado'])
        return JsonResponse({'ok': True})
    except Videos.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Video no existe'}, status=404)