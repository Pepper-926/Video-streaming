import os #Para trabajar con paths y nombres de archivos
from django.shortcuts import render, redirect
from .models import Videos, VideosEtiquetas, Etiquetas
from canales.models import Canales
from .forms import VideoUploadForm #Obtener form que se devuelve al cliente
from django.conf import settings #Para obtener el MEDIA_PATH
from .querys import asociar_etiquetas
from .tasks import convertir_video_a_hls

def index(request):
    return render(request, 'inicio.html')

def form_video(request):
    form = VideoUploadForm()
    return render(request, 'video.html', {'form': form})

def subir_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar archivo de video
            video_file = form.cleaned_data['file']
            video_path = os.path.join(settings.MEDIA_ROOT, 'videos', video_file.name)
            with open(video_path, 'wb+') as destination:
                for chunk in video_file.chunks():
                    destination.write(chunk)

            # Guardar miniatura si hay
            thumbnail_path = None
            thumbnail = form.cleaned_data.get('thumbnail')
            if thumbnail:
                thumbnail_path = os.path.join('imagenes', thumbnail.name)
                with open(os.path.join(settings.MEDIA_ROOT, thumbnail_path), 'wb+') as destination:
                    for chunk in thumbnail.chunks():
                        destination.write(chunk)

            #Temporal: usar canal 1 mientras no exista app de usuarios. Cuando funcionen las sesion hay que obtener el id del canal
            video = Videos.objects.create(
                link=video_path,
                titulo=form.cleaned_data['title'],
                descripcion=form.cleaned_data['description'],
                miniatura=thumbnail_path,
                id_canal=Canales.objects.get(id_canal=1)
            )

            # Carpeta de salida: media/stream/{video.id}
            carpeta_salida = os.path.join(settings.MEDIA_ROOT, 'stream', str(video.id_video))

            convertir_video_a_hls.delay(video.id, video_path)

            # Procesar etiquetas (checkboxes seleccionados)
            etiquetas_seleccionadas = form.cleaned_data['tags']
            asociar_etiquetas(video, etiquetas_seleccionadas)

            return redirect('/')
    else:
        return redirect('/videos/upload')
