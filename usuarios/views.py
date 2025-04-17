from django.shortcuts import render, redirect
from .models import Usuarios, Roles
from datetime import datetime

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
            fecha_nacimiento = datetime.strptime(nacimiento, '%Y-%m-%d')
            hoy = datetime.today()
            edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if edad < 13:
                return render(request, 'login.html')
        except ValueError:
            return render(request, 'login.html')

        # Verificación de contraseña
        if contra != confirmar_contra:
            return render(request, 'login.html')

        if not terminos:
            return render(request, 'login.html')

        # Verifica si el correo ya existe
        if Usuarios.objects.filter(correo=correo).exists():
            return render(request, 'login.html')

        # Obtener el rol "Usuario"
        try:
            rol = Roles.objects.get(rol='Usuario')
        except Roles.DoesNotExist:
            return render(request, 'login.html')

        # Guardar el usuario
        nuevo_usuario = Usuarios(
            nombre_canal=nombre_canal,
            nombre=nombre,
            a_pat=a_pat,
            a_mat=a_mat,
            nacimiento=nacimiento,
            correo=correo,
            contra=contra,  # en producción deberías encriptarla
            foto_perfil=foto_perfil.name if foto_perfil else None,
            id_rol=rol
        )
        nuevo_usuario.save()

        return redirect('login')  # Cambia 'login' por la vista a la que quieras redirigir

    return render(request, 'login.html')

