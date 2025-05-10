from django.urls import path
from . import views

urlpatterns = [
    path('paneladmin/', views.panel_admin, name='paneladmin'),
    path('videos/approve/<int:video_id>/', views.approve_video, name='approve_video'),
    path('cambiar-rol/<int:usuario_id>/', views.cambiar_rol, name='cambiar_rol'),
    path('eliminar-usuario/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
]