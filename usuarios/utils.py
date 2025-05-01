import jwt
import datetime
from django.conf import settings
import hashlib

def generar_token(usuario):
    # Crear token JWT
    payload = {
             'id_usuario': usuario.id_usuario,
             'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),  # expira en 1 hora
             'iat': datetime.datetime.now(datetime.timezone.utc)
            }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return token

def generar_hash(contra):
    # Genera el hash SHA-256 de la contraseña
    sha256_hash = hashlib.sha256(contra.encode()).hexdigest()
    return sha256_hash