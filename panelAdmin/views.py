from django.shortcuts import render, redirect
from videos.decoradores import verificar_token
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from videos.decoradores import verificar_token
from videos.models import Videos
from usuarios.models import Usuarios, Roles

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
    if request.usuario.id_rol.id_rol != 1:  
        return redirect('/')

    try:
        usuario = Usuarios.objects.get(id_usuario=usuario_id)
        rol = Roles.objects.get(id_rol=request.POST['rol'])  

        usuario.id_rol = rol
        usuario.save()

        return redirect('videos_pendientes') 

    except Usuarios.DoesNotExist:
        return redirect('videos_pendientes')  
    except Roles.DoesNotExist:
        return redirect('videos_pendientes')  
    
def listar_usuarios(request):
    usuarios = Usuarios.objects.all()

    roles = Roles.objects.all()

    return render(request, 'paneladmin.html', {'usuarios': usuarios, 'roles': roles})

@verificar_token
def eliminar_usuario(request, usuario_id):
    if request.usuario.id_rol.id_rol != 1: 
        return redirect('/')

    try:
        usuario = Usuarios.objects.get(id_usuario=usuario_id)

        usuario.delete()

        return redirect('videos_pendientes')  
    except Usuarios.DoesNotExist:
        return redirect('videos_pendientes')  
