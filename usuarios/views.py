import secrets
import datetime
from django.shortcuts import render, redirect
from django.conf import settings
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.utils import timezone
from videos.decoradores import verificar_token
from usuarios.models import Usuarios, Roles, Canales, PasswordResetToken, Seguidores
from videos.models import Videos
from .utils import generar_token, generar_hash

from django.views.decorators.csrf import csrf_exempt #para pruebas


def solicitar_recuperacion(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        
        try:
            # Obtener el usuario
            usuario = Usuarios.objects.get(correo=correo)

            # Generar un token único de recuperación
            token = secrets.token_urlsafe(32)  # Genera un token aleatorio y seguro

            # Crear un registro del token en la base de datos
            token_registro = PasswordResetToken.objects.create(
                id_usuario=usuario,
                token=token,
                created_at=timezone.now(),
                is_used=False
            )

            # Enviar el correo con el enlace de recuperación
            recovery_url = f"{settings.SITE_URL}/recuperar/{token}/"  # Asegúrate de que SITE_URL esté configurado correctamente

            send_mail(
                'Recuperación de contraseña',
                f'Para recuperar tu contraseña, haz clic en el siguiente enlace: {recovery_url}',
                'no-reply@miapp.com',
                [correo],
                fail_silently=False,
            )

            return render(request, 'recuperar_contrasena.html', {'aviso': 'Correo enviado, revíselo'})
        
        except Usuarios.DoesNotExist:
            return render(request, 'recuperar_contrasena.html', {'error': 'Correo no registrado'})

    return render(request, 'recuperar_contrasena.html')

def cambiar_contrasena(request, token):
    try:
        # Verificar el token
        token_obj = PasswordResetToken.objects.get(token=token, is_used=False)

        # Verificar si el token ha expirado (ejemplo: 1 hora de validez)
        if (timezone.now() - token_obj.created_at).total_seconds() > 3600:  # 1 hora
            return redirect('solicitar_recuperacion', {'error': 'El token ha expirado.'})

        if request.method == 'POST':
            nueva_contrasena = request.POST['nueva_contrasena']
            confirmacion_contrasena = request.POST['confirmacion_contrasena']

            if nueva_contrasena != confirmacion_contrasena:
                return render(request, 'cambiar_contrasena.html', {'error': 'Las contraseñas no coinciden'})

            # Cambiar la contraseña del usuario
            usuario = token_obj.id_usuario
            usuario.contra = generar_hash(nueva_contrasena)
            usuario.save()

            # Marcar el token como usado
            token_obj.is_used = True
            token_obj.save()

            return redirect('login')  # Redirigir al login después de actualizar la contraseña

        return render(request, 'cambiar_contrasena.html')

    except PasswordResetToken.DoesNotExist:
        return redirect('solicitar_recuperacion', {'error': 'Token inválido o ya utilizado.'})

def login(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        contra = request.POST['contra']

        try:
            usuario = Usuarios.objects.get(correo=correo)
            contra_hash = generar_hash(contra)

            if contra_hash == usuario.contra:
                token = generar_token(usuario)
                response = redirect('/')
                response.set_cookie('jwt', token, httponly=True, max_age=3600)
                return response
            else:
                return render(request, 'login.html', {'error': 'Credenciales inválidas'})
        except Usuarios.DoesNotExist:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})

    return render(request, 'login.html')


def registrar_usuario(request):
    if request.method == 'POST':
        # Captura de datos
        nombre_canal = request.POST.get('nombre_canal')
        nombre = request.POST.get('nombre')
        a_pat = request.POST.get('a_pat') or None
        a_mat = request.POST.get('a_mat') or None
        nacimiento = request.POST.get('nacimiento')
        correo = request.POST.get('correo')
        contra = request.POST.get('contra')
        confirmar_contra = request.POST.get('confirmar_contrasena')
        foto_perfil = request.FILES.get('foto_perfil')
        terminos = request.POST.get('terminos')

        #Verificacion de canal existente
        if Canales.objects.filter(nombre_canal = nombre_canal).exists():
            return render(request, 'registro.html', {'error': 'El nombre de canal ya está en uso.'})
        print('validó canal')

        # Validación de edad mínima (13 años)
        try:
            fecha_nacimiento = datetime.datetime.strptime(nacimiento, '%Y-%m-%d')
            hoy = datetime.datetime.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if edad < 13:
                return render(request, 'registro.html', {'error': 'Debes tener al menos 13 años para registrarte'})
        except ValueError:
            return render(request, 'registro.html', {'error': 'Fecha de nacimiento inválida. Asegúrate de usar un formato correcto (DD/MM/YYYY).'})
        
         # Verifica si el correo ya existe
        if Usuarios.objects.filter(correo=correo).exists():
            return render(request, 'registro.html', {'error': 'El correo electrónico ya está registrado.'})
        print('validó correo')

        # Verificación de contraseña
        if contra != confirmar_contra:
            return render(request, 'registro.html', {'error': 'Las contraseñas no coinciden.'})
        print('validó contra')

        if not terminos:
            return render(request, 'registro.html', {'error': 'Debes aceptar los términos y condiciones.'})


        # Obtener el rol "Usuario"
        try:
            rol = Roles.objects.get(id_rol=2)
        except Roles.DoesNotExist:
            return render(request, 'registro.html', {'error': 'No se pudo asignar el rol de usuario. Intenta de nuevo.'})
        
        # Generar el hash de la contraseña
        contra_hash = generar_hash(contra)

        # Guardar el usuario y canal
        nuevo_usuario = Usuarios(
            nombre=nombre,
            a_pat=a_pat,
            a_mat=a_mat,
            nacimiento=nacimiento,
            correo=correo,
            contra=contra_hash, 
            foto_perfil=foto_perfil.name if foto_perfil else None,
            id_rol=rol
        )

        nuevo_usuario.save()
        
        nuevo_canal = Canales(
            nombre_canal = nombre_canal,
            id_usuario = nuevo_usuario
        )
        
        print(f"Datos recibidos: {nuevo_usuario.nombre}, {nuevo_canal.nombre_canal}, {correo}")

        nuevo_canal.save()

        token = generar_token(nuevo_usuario)

        response = redirect('login')
        '''
        response.set_cookie(
                key='jwt',
                value=token,
                httponly=True,
                max_age=3600
            )
        '''
        return response
    return render(request, 'registro.html')

def logout(request):
    response = redirect('login')  # Redirige al login
    response.delete_cookie('jwt')  # Borra la cookie del token JWT
    return response


"""
API /usuarios/seguir-autor-por-video/{video_id}
"""
@method_decorator(verificar_token, name='dispatch')
#@method_decorator(verificar_token, name='delete')
class SeguirPorVideo(View):
    def get(self, request, video_id):
        try:
            video = Videos.objects.get(id_video=video_id)
            usuario_objetivo = video.id_canal.id_usuario
            usuario_actual = request.usuario

            ya_sigue = Seguidores.objects.filter(
                usuario=usuario_objetivo,
                seguidor=usuario_actual
            ).exists()

            total_seguidores = Seguidores.objects.filter(usuario=usuario_objetivo).count()

            return JsonResponse({
                'ok': True,
                'siguiendo': ya_sigue,
                'seguidores': total_seguidores
            }, status=200)

        except Videos.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Video no encontrado.'}, status=404)

        except Exception as e:
            print(f'get Seguir por videos: {e}')
            return JsonResponse({'ok': False, 'message': str(e)}, status=500)
        
    def post(self, request, video_id):
            try:
                video = Videos.objects.get(id_video=video_id)
                usuario_objetivo = video.id_canal.id_usuario
                usuario_actual = request.usuario

                if usuario_objetivo == usuario_actual:
                    return JsonResponse({'ok': False, 'message': 'No puedes seguirte a ti mismo.'}, status=400)

                _, creado = Seguidores.objects.get_or_create(
                    usuario=usuario_objetivo,
                    seguidor=usuario_actual
                )

                return JsonResponse({'ok': True, 'seguido': creado}, status=201 if creado else 200)

            except Videos.DoesNotExist:
                return JsonResponse({'ok': False, 'message': 'Video no encontrado.'}, status=404)

            except Exception as e:
                print(f'post Seguir por videos: {e}')
                return JsonResponse({'ok': False, 'message': str(e)}, status=500)
            
    def delete(self, request, video_id):
        try:
            video = Videos.objects.get(id_video=video_id)
            usuario_objetivo = video.id_canal.id_usuario
            usuario_actual = request.usuario

            if usuario_objetivo == usuario_actual:
                return JsonResponse({'ok': False, 'message': 'No puedes dejar de seguirte a ti mismo.'}, status=400)

            eliminado, _ = Seguidores.objects.filter(
                usuario=usuario_objetivo,
                seguidor=usuario_actual
            ).delete()

            if eliminado:
                return JsonResponse({'ok': True, 'message': 'Dejaste de seguir al autor.'}, status=200)
            else:
                return JsonResponse({'ok': False, 'message': 'No lo estabas siguiendo.'}, status=404)

        except Videos.DoesNotExist:
            return JsonResponse({'ok': False, 'message': 'Video no encontrado.'}, status=404)

        except Exception as e:
            print(f'Delete Seguir por videos: {e}')
            return JsonResponse({'ok': False, 'message': str(e)}, status=500)

