import os
from django.shortcuts import render, redirect
from .models import Videos, VideosEtiquetas, Etiquetas
from .forms import VideoUploadForm
from django.conf import settings

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
            video_path = os.path.join('videos', video_file.name)
            with open(os.path.join(settings.MEDIA_ROOT, video_path), 'wb+') as destination:
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

            # Crear registro en la base de datos con solo lo necesario
            video = Videos.objects.create(
                link=video_path,
                titulo=form.cleaned_data['title'],
                descripcion=form.cleaned_data['description'],
                miniatura=thumbnail_path,
                id_canal=request.user.canal.id  # suponiendo que el user está relacionado con el canal
            )

            # Procesar etiquetas (checkboxes seleccionados)
            etiquetas_seleccionadas = form.cleaned_data['tags']
            for etiqueta in etiquetas_seleccionadas:
                VideosEtiquetas.objects.create(id_video=video, id_etiqueta=etiqueta)


            return redirect('/')  # redirige según tu flujo
    else:
        return redirect('/videos/upload')