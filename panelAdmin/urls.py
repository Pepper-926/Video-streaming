from django.urls import path
from . import views

urlpatterns = [
    path('paneladmin/', views.panel_admin, name='paneladmin'),
    path('videos/approve/<int:video_id>/', views.approve_video, name='approve_video'),
    path('obtener_usuarios/', views.obtener_usuarios, name='obtener_usuarios'),
    path('/eliminar_usuario_y_canal/<int:usuario_id>/', views.eliminar_usuario_y_canal, name='eliminar_usuario_y_canal'),
    path('videos/usuario/<int:usuario_id>/', views.eliminar_videos_usuario, name='eliminar_videos_usuario'),
    path('usuarios/cambiar_rol/<int:usuario_id>/', views.cambiar_rol, name='cambiar_rol'),

]