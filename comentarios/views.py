import json
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from videos.models import Videos
from videos.utils import strtobool
from usuarios.models import Usuarios
from services.s3_storage import S3Manager
from .models import Comentarios
from .decoradores import verificar_token, intentar_verificar_token
from .utils import ajustar_hora

# Create your views here.
"""
Esta es la API /comentarios
"""
@method_decorator(intentar_verificar_token, name='get')
@method_decorator(verificar_token, name='post')
@method_decorator(verificar_token, name='delete')
class ViewComentarios(View):
    def get(self, request):
            try:
                s3 = S3Manager()
                filtros = {}

                # video_id opcional (si tú quieres que sea obligatorio, puedes volver a incluir la validación)
                if 'video_id' in request.GET:
                    filtros['id_video'] = request.GET['video_id']

                if 'id_usuario' in request.GET:
                    filtros['id_usuario'] = request.GET['id_usuario']

                if 'id_respuesta' in request.GET:
                    if request.GET['id_respuesta'].lower() == 'null':
                        filtros['id_respuesta__isnull'] = True
                    else:
                        filtros['id_respuesta'] = request.GET['id_respuesta']
                else:
                    filtros['id_respuesta__isnull'] = True  # solo comentarios principales por defecto

                # 👇 Analizar si el usuario es admin
                es_admin = (
                    hasattr(request, 'usuario') and
                    request.usuario and
                    hasattr(request.usuario, 'id_rol') and
                    request.usuario.id_rol.rol == 'admin'
                )

                # 👇 Si el usuario no es admin, forzar revisado=True
                if not es_admin:
                    filtros['revisado'] = True
                else:
                    # Si es admin y quiere filtrar por revisado manualmente, se respeta
                    if 'revisado' in request.GET:
                        try:
                            filtros['revisado'] = strtobool(request.GET['revisado'])
                        except ValueError:
                            return JsonResponse({'error': 'Parámetro "revisado" debe ser true o false'}, status=400)

                comentarios = Comentarios.objects.filter(**filtros).order_by('-fecha_comentado')

                data = [
                    {
                        'id_comentario': c.id_comentario,
                        'texto': c.texto,
                        'fecha': ajustar_hora(c.fecha_comentado),
                        'usuario': c.id_usuario.nombre,
                        'id_usuario': c.id_usuario.id_usuario,
                        'foto_perfil': s3.get_object_auto_mime(c.id_usuario.foto_perfil),
                        'respuestas': [
                            {
                                'id_comentario': r.id_comentario,
                                'texto': r.texto,
                                'fecha': ajustar_hora(r.fecha_comentado),
                                'usuario': r.id_usuario.nombre,
                                'id_usuario': r.id_usuario.id_usuario,
                                'foto_perfil': s3.get_object_auto_mime(r.id_usuario.foto_perfil),
                            }
                            for r in Comentarios.objects.filter(id_respuesta=c.id_comentario).order_by('-fecha_comentado')
                        ]
                    }
                    for c in comentarios
                ]

                return JsonResponse({
                    'comentarios': data,
                    'tu_id': request.usuario.id_usuario if hasattr(request, 'usuario') and request.usuario else None,
                    'num_comentarios': Comentarios.objects.filter(**filtros).count() if 'id_video' in filtros else None
                }, status=200)

            except Exception as e:
                print("Error al obtener comentarios:", str(e))
                return JsonResponse({'error': str(e)}, status=400)
        
    def post(self, request):
        try:
            data = json.loads(request.body)

            id_video = data.get("id_video")
            text = data.get("contenido")
            id_usuario = request.usuario.id_usuario
            id_respuesta = data.get("id_respuesta")  # Puede ser None

            nuevo_comentario = Comentarios(
                texto=text,
                id_video=Videos.objects.get(id_video=id_video),
                id_usuario=Usuarios.objects.get(id_usuario=id_usuario)
            )

            if id_respuesta:  # Solo si viene en la petición
                nuevo_comentario.id_respuesta = Comentarios.objects.get(id_comentario=id_respuesta)

            nuevo_comentario.save()

            return JsonResponse({"mensaje": "Datos recibidos correctamente"}, status=200)

        except Exception as e:
            print("Error al procesar comentario:", str(e))
            return JsonResponse({"error": str(e)}, status=400)

        
    def delete(self, request):
        try:
            id_comentario = request.GET.get('id_comentario')
            if not id_comentario:
                return JsonResponse({'error': 'Falta id del comentario.'}, status=400)
            
            comentario = Comentarios.objects.get(id_comentario=id_comentario)
            print("Usuario autenticado:", request.usuario.id_usuario)
            print("Rol:", request.usuario.id_rol.rol)
            print("Dueño del comentario:", comentario.id_usuario.id_usuario)
            if request.usuario != comentario.id_usuario and request.usuario.id_rol.rol != 'admin':
                return JsonResponse({'error':'Sin permisos para este recurso'}, status=403)

            comentario.delete()
            return JsonResponse({'ok':True,'message':'Se elimino el comentario.'}, status=200)
        
        except Comentarios.DoesNotExist:
            return JsonResponse({'error': 'Comentario no encontrado.'}, status=404)
        
        except Exception as e:
            print(e)
            return JsonResponse({'error':str(e)}, status=500)