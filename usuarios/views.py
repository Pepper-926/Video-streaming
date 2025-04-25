from django.shortcuts import render, redirect
from usuarios.models import Usuarios, Roles, Canales
import datetime
import jwt
from django.conf import settings


def inicio(request):
    return render(request, 'inicio.html')

def login(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        contra = request.POST['contra']

        try:
            usuario = Usuarios.objects.get(correo=correo, contra=contra)

            # Crear token JWT
            payload = {
                'id_usuario': usuario.id_usuario,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),  # expira en 1 hora
                'iat': datetime.datetime.now(datetime.timezone.utc)
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

            # Crear respuesta y guardar el token en una cookie segura
            response = redirect('inicio')
            response.set_cookie(
                key='jwt',
                value=token,
                httponly=True,  # Importante para que el token no sea accesible desde JavaScript
                max_age=3600
            )

            return response

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

        # Validación de edad mínima (13 años)
        try:
            fecha_nacimiento = datetime.datetime.strptime(nacimiento, '%Y-%m-%d')
            hoy = datetime.datetime.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if edad < 13:
                return render(request, 'registro.html')
        except ValueError:
            return render(request, 'registro.html')

        # Verificación de contraseña
        if contra != confirmar_contra:
            return render(request, 'registro.html')
        print('validacion hecha contra')

        if not terminos:
            return render(request, 'registro.html')

        # Verifica si el correo ya existe
        if Usuarios.objects.filter(correo=correo).exists():
            return render(request, 'registro.html')
        print('valida correo')

        # Obtener el rol "Usuario"
        try:
            rol = Roles.objects.get(id_rol=2)
        except Roles.DoesNotExist:
            return render(request, 'registro.html')
        

        # Guardar el usuario y canal
        nuevo_usuario = Usuarios(
            nombre=nombre,
            a_pat=a_pat,
            a_mat=a_mat,
            nacimiento=nacimiento,
            correo=correo,
            contra=contra, 
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

        return redirect('registrar_usuario') 

    return render(request, 'registro.html')

def logout(request):
    response = redirect('login')  # Redirige al login
    response.delete_cookie('jwt')  # Borra la cookie del token JWT
    return response



