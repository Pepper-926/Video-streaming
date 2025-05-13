import json
from django.shortcuts import render, redirect
from videos.decoradores import verificar_token
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from videos.decoradores import verificar_token
from videos.models import Videos
from usuarios.models import Usuarios, Roles, Canales
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction

@verificar_token
def panel_admin(request):
    if request.usuario and request.usuario.id_rol.rol == 'admin': #Proteccion para que solo un admin pueda acceder a la vista
        return render(request, 'paneladmin.html')
    else:
        return redirect('/')

@verificar_token
def approve_video(request, video_id):
    if request.usuario.id_rol.id_rol != 1:  # Asegurarse de que sea administrador
        return JsonResponse({'success': False, 'message': 'Acción no permitida.'})

    
    try:
        video = Videos.objects.get(id_video=video_id)

        
        video.revisado = True
        video.save()
        return JsonResponse({'success': True, 'message': 'Video aprobado.'})

    except Videos.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Video no encontrado.'})

@verificar_token
def cambiar_rol(request, usuario_id):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)

    if request.usuario.id_rol.id_rol != 1:  # Solo admin puede cambiar roles
        return JsonResponse({'success': False, 'message': 'No autorizado'}, status=403)

    try:
        # Leer el JSON del body
        data = json.loads(request.body)
        nuevo_rol = data.get('rol')

        if not nuevo_rol:
            return JsonResponse({'success': False, 'message': 'No se recibió el nuevo rol'}, status=400)

        usuario = Usuarios.objects.get(id_usuario=usuario_id)
        rol = Roles.objects.get(rol=nuevo_rol)  # O usa id_rol si estás mandando un número

        usuario.id_rol = rol
        usuario.save()

        return JsonResponse({'success': True, 'message': 'Rol actualizado correctamente'})

    except Usuarios.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Usuario no encontrado'}, status=404)

    except Roles.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Rol no válido'}, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Error al leer los datos JSON'}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@verificar_token
def eliminar_usuario_y_canal(request, usuario_id):
    if request.usuario.id_rol.rol != 'admin':
        return JsonResponse({'success': False, 'message': 'Acción no permitida.'})

    try:
        with transaction.atomic():
            # Obtener usuario y canal
            usuario = get_object_or_404(Usuarios, id_usuario=usuario_id)
            canal = get_object_or_404(Canales, id_usuario=usuario)

            # Obtener videos del canal
            videos = Videos.objects.filter(id_canal=canal)

            # Eliminar videos uno por uno (esto sí activa post_delete y lógica adicional)
            for video in videos:
                # Eliminar video
                video.delete()

            # Eliminar canal
            canal.delete()

            # Eliminar usuario
            usuario.delete()

            return JsonResponse({'success': True, 'message': 'Usuario y canal eliminados correctamente.'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@verificar_token
def obtener_usuarios(request):
    # Obtener el número de página desde los parámetros GET, por defecto es la página 1
    page_number = request.GET.get('page', 1)

    # Recuperamos todos los usuarios
    usuarios_list = Usuarios.objects.all()

    # Crear un objeto Paginator que dividirá los usuarios en páginas
    paginator = Paginator(usuarios_list, 3)  # 3 usuarios por página

    try:
        # Obtener los usuarios de la página solicitada
        usuarios = paginator.page(page_number)
    except Exception as e:
        # Si no se encuentra la página, se pueden manejar errores
        return JsonResponse({'error': 'Página no válida'}, status=400)

    # Crear la respuesta JSON con los usuarios
    usuarios_data = []
    for usuario in usuarios:
        usuarios_data.append({
            'id_usuario': usuario.id_usuario,
            'nombre': usuario.nombre,
            'correo': usuario.correo,
            'rol': usuario.id_rol.rol,  # Asumiendo que el rol está relacionado
        })

    return JsonResponse({'usuarios': usuarios_data})