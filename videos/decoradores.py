import jwt
from django.conf import settings
from django.http import JsonResponse
from usuarios.models import Usuarios
from functools import wraps

def verificar_token(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('jwt')

        if not token:
            return JsonResponse({'error': 'No autenticado'}, status=401)

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            usuario = Usuarios.objects.get(id_usuario=payload['id_usuario'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token expirado'}, status=401)
        except (jwt.DecodeError, Usuarios.DoesNotExist):
            return JsonResponse({'error': 'Token inválido'}, status=401)

        request.usuario = usuario

        return func(request, *args, **kwargs)

    return wrapper