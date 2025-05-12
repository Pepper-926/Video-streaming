from datetime import timedelta
from django.utils import timezone
import locale
from .models import Comentarios


def serializar_comentario(comentario):
    if comentario is None:
        print("Comentario es None")
        return {}

    print(f"Serializando comentario ID {comentario.id_comentario}")

    if not hasattr(comentario, 'id_usuario') or comentario.id_usuario is None:
        print(f"Comentario {comentario.id_comentario} no tiene usuario asignado")
        return {
            'id_comentario': comentario.id_comentario,
            'texto': comentario.texto,
            'fecha': comentario.fecha_comentado.strftime('%Y-%m-%d %H:%M'),
            'usuario': 'Usuario eliminado',
            'id_usuario': None,
            'foto_perfil': None,
            'respuestas': []
        }

    comentario_dict = {
        'id_comentario': comentario.id_comentario,
        'texto': comentario.texto,
        'fecha': comentario.fecha_comentado.strftime('%Y-%m-%d %H:%M'),
        'usuario': comentario.id_usuario.nombre,
        'id_usuario': comentario.id_usuario.id_usuario,
        'foto_perfil': comentario.id_usuario.foto_perfil,
        'respuestas': []
    }

    respuestas = Comentarios.objects.filter(id_respuesta=comentario.id_comentario).order_by('-fecha_comentado')
    for r in respuestas:
        try:
            serializado = serializar_comentario(r)
            if serializado:
                comentario_dict['respuestas'].append(serializado)
        except Exception as e:
            print(f"Error serializando respuesta ID {r.id_comentario}: {e}")

    return comentario_dict

MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
}

def ajustar_hora(fecha):
    if timezone.is_naive(fecha):
        fecha = fecha + timedelta(hours=-6)
    else:
        fecha = timezone.localtime(fecha)

    return f"{fecha.day} de {MESES_ES[fecha.month]} de {fecha.year}, {fecha.strftime('%H:%M')}"

