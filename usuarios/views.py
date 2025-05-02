from django.shortcuts import render, redirect
from usuarios.models import Usuarios, Roles, Canales
import datetime
from django.conf import settings
from .utils import generar_token, generar_hash
from django.contrib.auth.hashers import make_password, check_password

def login(request):
    if request.method == 'POST':
        correo = request.POST['correo']
        contra = request.POST['contra']

        try:
            usuario = Usuarios.objects.get(correo=correo)
            contra_hash = generar_hash(contra)

            if contra_hash == usuario.contra:
                token = generar_token(usuario)
                response = redirect('index')
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

        response = redirect('registro')
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



