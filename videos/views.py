import json
import os  # Para trabajar con paths y nombres de archivos
import shutil  # Para eliminar directorios completos
from datetime import timedelta
from django.conf import settings  # Para obtener el MEDIA_PATH
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from .decoradores import verificar_token, intentar_verificar_token
from .forms import VideoUploadForm, SearchForm # Obtener form que se devuelve al cliente
from .models import Videos, EtiquetasDeVideos, VistaCanalDeVideo, Historial, VwDetalleVideo, Etiquetas, LikesDislikesVideos
from .querys import asociar_etiquetas
from .tasks import convertir_video_a_hls
from .utils import optimizar_imagen, strtobool
from services.s3_storage import S3Manager
from usuarios.models import Canales
from comentarios.models import Comentarios

from django.views.decorators.csrf import csrf_exempt #para pruebas


'''
Views que devuelven HTMLs
'''
@intentar_verificar_token
def index(request):
    form = SearchForm()
    return render(request, 'inicio.html', {
        'permisos': True if request.usuario and request.usuario.id_rol.rol == 'admin' else None,
        'search_form': form
    })

@verificar_token
def form_video(request):
    form = VideoUploadForm()
    return render(request, 'video.html', {'form': form})

#View donde el usuario sube el video.
@verificar_token
def confirmar_subida(request, video_id):
    return render(request, 'video_subida.html', {'video_id': video_id})

#View para visualizar el video junto sus comentarios
@intentar_verificar_token
def ver_video(request, video_id):
    video = get_object_or_404(VwDetalleVideo, id_video=video_id)
    if not video.revisado:
        return JsonResponse({
            'ok': False,
            'message': 'El video aun no ha sido revisado por un administrador.',
        }, status=403)
    
    token_privado = request.GET.get('token')
    
    # Validación de visibilidad del video
    if not video.publico and token_privado != video.token_acceso_privado:
        return JsonResponse({'ok': False, 'message': 'Acceso no autorizado. El video es privado.'}, status=403)
    
    fecha_local = video.fecha_publicado + timedelta(hours=-6) 

    #Aqui se hace un conteo en la tabla historial para manejar el historial de cada usuario y cuantas visualizacion tiene cada video. SOLO SE CUENTA SI EL USUARIO ESTA AUTENTICADO. Tambien se hacen otras comprobaciones en caso de que este autenticado el usuario.

    try:
        if request.usuario:
            
            Historial.objects.create(
                id_usuario = request.usuario,
                id_video = Videos.objects.get(id_video=video_id)
            )

    except Exception as e:
        print(e)

    try:
        if video.miniatura:
            s3 = S3Manager()
            link_miniatura = s3.get_object(video.miniatura, content_type='image/jpeg')
        else:
            link_miniatura = None
    except Exception as e:
        print(e)

    try:
        etiquetas = Etiquetas.objects.filter(videosetiquetas__id_video=video_id)
        
    except Exception as e:
        print(e)

    return render(request, 'pagvideo.html', 
                  {'video': video,
                    'miniatura': link_miniatura,
                    'etiquetas': etiquetas,
                    'foto_perfil_canal': s3.get_object_auto_mime(video.foto_perfil),
                    'foto_perfil_usuario': s3.get_object_auto_mime(request.usuario.foto_perfil) if request.usuario else False,
                    'fecha_video': fecha_local
                    })

'''
Esta es la api /videos
'''
#Vista de /videos
@method_decorator(verificar_token, name='post')
@method_decorator(intentar_verificar_token, name='get')
class VideosView(View):
    def get(self, request):
        try:
            s3 = S3Manager()

            # Filtros booleanos opcionales
            filtros = {}
            booleanos = ['revisado', 'publico', 'estado', 'conversion_completa']
            for campo in booleanos:
                valor = request.GET.get(campo)
                if valor is not None:
                    filtros[campo] = valor.lower() == 'true'

            # Verificación de acceso si se pide filtrado restringido
            if any(k in filtros for k in ['revisado', 'publico', 'estado']):
                if not (request.usuario and request.usuario.id_rol.rol == 'admin'):
                    return JsonResponse({'ok': False, 'message': 'Solo un administrador puede aplicar estos filtros.'}, status=403)
            
            # Filtro base según el rol
            if request.usuario and request.usuario.id_rol.rol == 'admin':
                videos_query = Videos.objects.filter(**filtros)
            else:
                filtros.setdefault('publico', True)
                filtros.setdefault('revisado', True)
                videos_query = Videos.objects.filter(**filtros)

            # Filtro de búsqueda por 'titulo' (aplica a título, canal y descripción)
            query = request.GET.get('titulo')
            if query:
                videos_query = videos_query.filter(
                    Q(titulo__icontains=query) |
                    Q(id_canal__nombre_canal__icontains=query) |
                    Q(descripcion__icontains=query)
                )

            canal_map = {
                c.id_video: c for c in VistaCanalDeVideo.objects.filter(publico=True)
            }

            data = []
            for v in videos_query:
                canal_info = canal_map.get(v.id_video)
                data.append({
                    'id_video': v.id_video,
                    'titulo': v.titulo,
                    'descripcion': v.descripcion,
                    'miniatura': s3.get_object(v.miniatura, content_type='image/jpeg') if v.miniatura else None,
                    'etiquetas': [
                        etiqueta.categoria
                        for etiqueta in EtiquetasDeVideos.objects.filter(id_video=v.id_video)
                    ],
                    'canal': canal_info.nombre_canal if canal_info else None,
                    'link': s3.get_object(v.link, content_type='application/vnd.apple.mpegurl') if v.link else None,
                    'foto_perfil': s3.get_object(canal_info.foto_perfil, content_type='image/jpeg') if canal_info and canal_info.foto_perfil else None 
                })

            return JsonResponse({'videos': data}, status=200)

        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)
    
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
        if form.cleaned_data['visibility'] == 'public':
            es_publico = True
            token = None
        else:
            es_publico = False
            token = get_random_string(48)

        video = Videos.objects.create(
            link      = '',
            miniatura = '',
            titulo    = form.cleaned_data['title'],
            descripcion = form.cleaned_data['description'],
            publico   = es_publico,
            id_canal  = canal,
            token_acceso_privado = token
        )

        # 3 ─── Construir rutas DEFINITIVAS usando id_video ────────────────
        vid_dir = f"videos/video{video.id_video}"
        os.makedirs(os.path.join(settings.MEDIA_ROOT, vid_dir), exist_ok=True)

        final_video_rel = f"{vid_dir}/index.m3u8"

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

        transaction.on_commit(lambda: convertir_video_a_hls.delay(video.id_video, final_src_mp4_fs))    

        # etiquetas
        asociar_etiquetas(video, form.cleaned_data['tags'])

        return redirect(f'/videos/subida/{video.id_video}')
    
'''
Esta es la api /videos/<id>
'''
@method_decorator(verificar_token, name='delete')
@method_decorator(verificar_token, name='put')
@method_decorator(csrf_exempt, name='dispatch')
class VideoDetailsViews(View):
    def get(self, request, video_id):
        try:
            s3 = S3Manager()
            video = Videos.objects.get(id_video=video_id)

            # Buscar canal asociado desde la vista
            canal_info = VistaCanalDeVideo.objects.filter(id_video=video_id).first()

            data = {
                'id_video': video.id_video,
                'titulo': video.titulo,
                'descripcion': video.descripcion,
                'link': s3.get_object(video.link, content_type='application/vnd.apple.mpegurl') if video.link else None,
                'miniatura': s3.get_object(video.miniatura, content_type='image/jpeg') if video.miniatura else None,
                'etiquetas': [
                    etiqueta.categoria
                    for etiqueta in EtiquetasDeVideos.objects.filter(id_video=video.id_video)
                ],
                'canal': canal_info.nombre_canal if canal_info else None,
                'foto_perfil': s3.get_object(canal_info.foto_perfil, content_type='image/jpeg') if canal_info and canal_info.foto_perfil else None
            }
            return JsonResponse(data, status=200)            
       
        except Exception as e:
           return JsonResponse({'error': str(e)}, status=500)

    def delete(self, request, video_id):
            try:
                # Eliminar objeto en la base de datos
                video = Videos.objects.get(id_video=video_id)
                video.delete()
                return JsonResponse({'ok': True})

            except Videos.DoesNotExist:
                raise Http404("Video no encontrado")

            except Exception as e:
                return JsonResponse({'ok': False, 'error': str(e)}, status=500)

    def put(self, request, video_id):
        try:
            video = Videos.objects.get(id_video=video_id)

            #Verifica que el que lo quiere modificar sea el usuario duenio del video o un admin
            if request.usuario.id_rol.rol != 'admin' and video.id_canal.id_usuario != request.usuario:
                return JsonResponse({'ok': False, 'message': 'No tienes permiso para modificar este video'}, status=403)

            # Parsear el body del request (asumiendo que es JSON)
            body = json.loads(request.body)

            calificacion = body.get('calificacion')
            titulo = body.get('titulo')
            descripcion = body.get('descripcion')
            revisado = body.get('revisado')
            publico = body.get('publico')
            miniatura = body.get('miniatura')
            # Aún no se usa miniatura_img

            if calificacion is not None:
                video.calificacion = calificacion
            if titulo is not None:
                video.titulo = titulo
            if descripcion is not None:
                video.descripcion = descripcion
            if revisado is not None:
                if request.usuario.id_rol.rol == 'admin':
                    video.revisado = bool(strtobool(str(revisado)))
                else:
                    return JsonResponse({'ok':False,'message':f'Solo un administrador puede modificar el campo revisado. Tu rol es: {request.usuario.id_rol.rol}'})
            if publico is not None:
                video.publico = bool(strtobool(str(publico)))
            if miniatura is not None:
                video.miniatura = miniatura  # futura integración con S3

            video.save()
            return JsonResponse({
                'ok': True,
                'video': {
                    'id_video': video.id_video,
                    'titulo': video.titulo,
                    'descripcion': video.descripcion,
                    'calificacion': video.calificacion,
                    'publico': video.publico,
                    'revisado': video.revisado,
                    'miniatura': video.miniatura
                }
            }, status=200)

        except Exception as e:
            return JsonResponse({'ok': False, 'message': str(e)}, status=500)

'''
/videos/<int:video_id>/like/
'''
@method_decorator(intentar_verificar_token, name='get')
@method_decorator(verificar_token, name='post')
class LikesVideos(View):
    def get(self, request, video_id=None):
        if not video_id:
            return JsonResponse({
                'ok': False,
                'error': 'No se proporcionó un ID de video en la URL.'
            }, status=400)

        try:
            video = Videos.objects.get(id_video=video_id)
        except Videos.DoesNotExist:
            return JsonResponse({
                'ok': False,
                'error': f'No se encontró un video con id {video_id}.'
            }, status=404)

        cantidad_dislikes = LikesDislikesVideos.objects.filter(
            id_video=video,
            tipo_reaccion=False
        ).count()

        ya_dio_dislike = False
        if hasattr(request, 'usuario') and request.usuario:
            ya_dio_dislike = LikesDislikesVideos.objects.filter(
                id_video=video,
                id_usuario=request.usuario,
                tipo_reaccion=True
            ).exists()

        return JsonResponse({
            'ok': True,
            'likes': cantidad_dislikes,
            'liked': ya_dio_dislike
        })

    def post(self, request, video_id):
            try:
                usuario = request.usuario
                video = Videos.objects.get(id_video=video_id)

                reaccion_existente = LikesDislikesVideos.objects.filter(
                    id_usuario=usuario,
                    id_video=video,
                    tipo_reaccion=True
                ).first()

                if reaccion_existente:
                    reaccion_existente.delete()
                    liked = False
                else:
                    # Antes de crear un like, elimina cualquier dislike existente
                    LikesDislikesVideos.objects.filter(
                        id_usuario=usuario,
                        id_video=video,
                        tipo_reaccion=False  # elimina el like
                    ).delete()
                    LikesDislikesVideos.objects.create(
                        id_usuario=usuario,
                        id_video=video,
                        tipo_reaccion=True
                    )
                    liked = True

                cantidad_likes = LikesDislikesVideos.objects.filter(id_video=video, tipo_reaccion=True).count()
                cantidad_dislikes = LikesDislikesVideos.objects.filter(id_video=video, tipo_reaccion=False).count()
                return JsonResponse({'ok': True, 'liked': liked, 'likes': cantidad_likes, 'dislikes':cantidad_dislikes})

            except Exception as e:
                print(e)
                return JsonResponse({'ok': False, 'message': str(e)}, status=500)
            
'''
/videos/<int:video_id>/dislike/
'''
@method_decorator(intentar_verificar_token, name='get')
@method_decorator(verificar_token, name='post')
class DislikesVideos(View):
    def get(self, request, video_id=None):
        if not video_id:
            return JsonResponse({
                'ok': False,
                'error': 'No se proporcionó un ID de video en la URL.'
            }, status=400)

        try:
            video = Videos.objects.get(id_video=video_id)
        except Videos.DoesNotExist:
            return JsonResponse({
                'ok': False,
                'error': f'No se encontró un video con id {video_id}.'
            }, status=404)

        cantidad_dislikes = LikesDislikesVideos.objects.filter(
            id_video=video,
            tipo_reaccion=False
        ).count()

        ya_dio_dislike = False
        if hasattr(request, 'usuario') and request.usuario:
            ya_dio_dislike = LikesDislikesVideos.objects.filter(
                id_video=video,
                id_usuario=request.usuario,
                tipo_reaccion=False
            ).exists()

        return JsonResponse({
            'ok': True,
            'dislikes': cantidad_dislikes,
            'disliked': ya_dio_dislike
        })

    def post(self, request, video_id):
            try:
                usuario = request.usuario
                video = Videos.objects.get(id_video=video_id)

                reaccion_existente = LikesDislikesVideos.objects.filter(
                    id_usuario=usuario,
                    id_video=video,
                    tipo_reaccion=False
                ).first()

                if reaccion_existente:
                    reaccion_existente.delete()
                    liked = False
                else:
                    # Antes de crear un dislike, elimina cualquier like existente
                    LikesDislikesVideos.objects.filter(
                        id_usuario=usuario,
                        id_video=video,
                        tipo_reaccion=True  # elimina el like
                    ).delete()
                    LikesDislikesVideos.objects.create(
                        id_usuario=usuario,
                        id_video=video,
                        tipo_reaccion=False
                    )
                    liked = True

                cantidad_likes = LikesDislikesVideos.objects.filter(id_video=video, tipo_reaccion=True).count()
                cantidad_dislikes = LikesDislikesVideos.objects.filter(id_video=video, tipo_reaccion=False).count()
                return JsonResponse({'ok': True, 'disliked': liked, 'likes': cantidad_likes, 'dislikes':cantidad_dislikes})

            except Exception as e:
                print(e)
                return JsonResponse({'ok': False, 'message': str(e)}, status=500)





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
        s3 = S3Manager()
        urls = s3.generar_urls_firmadas_para_stream(video_id)
        return JsonResponse({'archivos': urls})
    except FileNotFoundError:
        return JsonResponse({'error': 'Video aún no procesado o no existe'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

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

def stream_m3u8(request, video_id):
    """
    Devuelve el contenido del index.m3u8 con URLs firmadas para los fragmentos .ts.
    """
    try:
        ruta = f"videos/video{video_id}/index.m3u8"
        s3 = S3Manager()
        contenido_modificado = s3.generar_m3u8_con_urls_firmadas(ruta)
        return HttpResponse(contenido_modificado, content_type='application/vnd.apple.mpegurl')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)