from functools import wraps
from django.http import JsonResponse
from django.conf import settings
import jwt
from usuarios.models import Usuarios

def verificar_token(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('jwt')

        if not token:
            return JsonResponse({'error': 'Token no proporcionado'}, status=401)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            usuario = Usuarios.objects.get(id_usuario=payload['id_usuario'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)
        except (jwt.DecodeError, Usuarios.DoesNotExist):
            return JsonResponse({'error': 'Token inválido o usuario no encontrado'}, status=401)

        request.usuario = usuario
        return func(request, *args, **kwargs)

    return wrapper

def intentar_verificar_token(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('jwt')

        try:
            if token:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                usuario = Usuarios.objects.get(id_usuario=payload['id_usuario'])
                request.usuario = usuario  # Asignamos solo si es válido
            else:
                request.usuario = None
                
        except (jwt.ExpiredSignatureError, jwt.DecodeError, Usuarios.DoesNotExist):
            pass  # Ignoramos cualquier error y seguimos sin asignar `request.usuario`

        return func(request, *args, **kwargs)

    return wrapper