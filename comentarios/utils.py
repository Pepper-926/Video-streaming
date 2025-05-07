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
