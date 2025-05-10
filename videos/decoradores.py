import jwt
from django.conf import settings
from django.http import JsonResponse
from usuarios.models import Usuarios
from functools import wraps
from django.shortcuts import redirect

from django.http import JsonResponse
from functools import wraps
import jwt

def verificar_token(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        token = request.COOKIES.get('jwt')

        if not token:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'redirect': True}, status=401)
            return redirect('/login')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            usuario = Usuarios.objects.get(id_usuario=payload['id_usuario'])
        except (jwt.ExpiredSignatureError, jwt.DecodeError, Usuarios.DoesNotExist):
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'redirect': True}, status=401)
            return redirect('/login')

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