from django.shortcuts import render, get_object_or_404, redirect
from videos.decoradores import verificar_token
from django.http import JsonResponse
from videos.decoradores import verificar_token
from videos.models import Videos
from usuarios.models import Usuarios, Roles, Canales,Seguidores
from videos.models import Historial, LikesDislikesVideos, VideosEtiquetas
from comentarios.models import Comentarios
from django.core.paginator import Paginator
import json
from services.s3_storage import S3Manager
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
def eliminar_usuario_y_canal(request, usuario_id):
    if request.usuario.id_rol.id_rol != 1:  # Solo si es admin
        return JsonResponse({'success': False, 'message': 'Acción no permitida.'})

    try:
        with transaction.atomic():
            # Obtener al usuario
            usuario = get_object_or_404(Usuarios, id_usuario=usuario_id)
            canal = get_object_or_404(Canales, id_usuario=usuario)

            # Eliminar historial
            Historial.objects.filter(id_usuario=usuario).delete()

            # Eliminar seguidores
            Seguidores.objects.filter(seguidor=usuario).delete()

            # Eliminar videos y todo lo relacionado
            videos = Videos.objects.filter(id_canal=canal)
            for video in videos:
                LikesDislikesVideos.objects.filter(id_video=video).delete()
                VideosEtiquetas.objects.filter(id_video=video).delete()
                Comentarios.objects.filter(id_video=video).delete()
                video.delete()

            # Eliminar canal
            canal.delete()

            # Eliminar usuario
            usuario.delete()

            return JsonResponse({'success': True, 'message': 'Usuario y canal eliminados correctamente.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
@verificar_token
def eliminar_videos_usuario(request, usuario_id):
    try:
        # Obtener los videos del usuario
        videos = Videos.objects.filter(id_canal=usuario_id)

        # Crear instancia de S3Manager para manejar la eliminación en la nube
        s3 = S3Manager()

        # Eliminar cada video en la nube
        for video in videos:
            s3.delete_folder(f'videos/video{video.id_video}/')

        return JsonResponse({'success': True, 'message': 'Videos eliminados de la nube.'})
    
    except Videos.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'No se encontraron videos para eliminar.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

    
@verificar_token
def cambiar_rol(request, usuario_id):
    if request.usuario.id_rol.id_rol != 1:  # Solo si es admin
        return JsonResponse({'success': False, 'message': 'Acción no permitida.'})

    try:
        # Si el request es POST, entonces procesamos la información
        if request.method == 'POST':
            # Cargar el cuerpo de la solicitud como JSON
            data = json.loads(request.body)  # Parsear el JSON del cuerpo de la solicitud
            nuevo_rol = data.get('rol')  # Obtener el nuevo rol
            print(nuevo_rol)

            # Obtener al usuario
            usuario = Usuarios.objects.get(id_usuario=usuario_id)

            # Obtener el objeto 'Roles' basado en el nombre del rol
            rol_obj = Roles.objects.get(rol=nuevo_rol)

            # Asignar el nuevo rol al usuario
            usuario.id_rol = rol_obj
            usuario.save()

            return JsonResponse({'success': True, 'message': 'Rol actualizado exitosamente.'})

        else:
            return JsonResponse({'success': False, 'message': 'Método no permitido.'})

    except Usuarios.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Usuario no encontrado.'})

    except Roles.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Rol no encontrado.'})

    
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

