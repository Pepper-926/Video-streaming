import jwt
from django.conf import settings
from django.http import JsonResponse
from usuarios.models import Usuarios
from functools import wraps
from django.shortcuts import redirect

def verificar_token(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('jwt')

        if not token:
            return redirect('/login')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            usuario = Usuarios.objects.get(id_usuario=payload['id_usuario'])
        except jwt.ExpiredSignatureError:
            return redirect('/login')
        except (jwt.DecodeError, Usuarios.DoesNotExist):
            return redirect('/login')

        request.usuario = usuario

        return func(request, *args, **kwargs)

    return wrapper