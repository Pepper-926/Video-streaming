import json
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from videos.models import Videos
from usuarios.models import Usuarios
from .models import Comentarios
from .decoradores import verificar_token, intentar_verificar_token

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
            video_id = request.GET.get('video_id')

            if not video_id:
                return JsonResponse({'error': 'Parámetro video_id requerido'}, status=400)

            comentarios = Comentarios.objects.filter(id_video=video_id).filter(id_respuesta=None).order_by('-fecha_comentado')

            data = [
                {
                    'id_comentario': c.id_comentario,
                    'texto': c.texto,
                    'fecha': c.fecha_comentado.strftime('%Y-%m-%d %H:%M'),
                    'usuario': c.id_usuario.nombre,
                    'id_usuario': c.id_usuario.id_usuario,
                    'foto_perfil': c.id_usuario.foto_perfil,
                    'respuestas': [
                        {
                            'id_comentario': r.id_comentario,
                            'texto': r.texto,
                            'fecha': r.fecha_comentado.strftime('%Y-%m-%d %H:%M'),
                            'usuario': r.id_usuario.nombre,
                            'id_usuario': r.id_usuario.id_usuario,
                            'foto_perfil': r.id_usuario.foto_perfil,
                        }
                        for r in Comentarios.objects.filter(id_respuesta=c.id_comentario).order_by('-fecha_comentado') 
                    ]
                }
                for c in comentarios #if c.revisado == True #Descomentar esta linea cuando ya se pueda revisar comentarios.
            ]

            return JsonResponse({'comentarios': data,
                                 'tu_id': request.usuario.id_usuario if request.usuario else None,
                                 'num_comentarios':Comentarios.objects.filter(id_video=video_id).count()}, status=200)

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