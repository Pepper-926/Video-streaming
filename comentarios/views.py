import json
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from videos.models import Videos
from usuarios.models import Usuarios
from .models import Comentarios
from .decoradores import verificar_token

# Create your views here.
"""
Esta es la API /comentarios
"""
@method_decorator(verificar_token, name='post')
class ViewComentarios(View):
    def get(self, request):
        try:
            video_id = request.GET.get('video_id')

            if not video_id:
                return JsonResponse({'error': 'Parámetro video_id requerido'}, status=400)

            comentarios = Comentarios.objects.filter(id_video=video_id).order_by('-fecha_comentado')

            data = [
                {
                    'id_comentario': c.id_comentario,
                    'texto': c.texto,
                    'fecha': c.fecha_comentado.strftime('%Y-%m-%d %H:%M'),
                    'usuario': c.id_usuario.nombre,  # Asegúrate de tener este campo
                    'foto_perfil': c.id_usuario.foto_perfil,  # O ajusta según tu modelo
                }
                for c in comentarios
            ]

            return JsonResponse({'comentarios': data}, status=200)

        except Exception as e:
            print("Error al obtener comentarios:", str(e))
            return JsonResponse({'error': str(e)}, status=400)

    def post(self, request):
        try:
            data = json.loads(request.body)

            id_video = data.get("id_video")
            text = data.get("contenido")
            id_usuario = request.usuario.id_usuario
            Comentarios.objects.create(
                texto = text,
                id_video = Videos.objects.get(id_video=id_video),
                id_usuario = Usuarios.objects.get(id_usuario=id_usuario),
            )

            return JsonResponse({"mensaje": "Datos recibidos correctamente"}, status=200)

        except Exception as e:
            print("Error al procesar comentario:", str(e))
            return JsonResponse({"error": str(e)}, status=400)