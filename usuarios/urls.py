from django.urls import path
from . import views


urlpatterns  = [
    path('registro/', views.registrar_usuario, name = 'registrar_usuario'),
    path('login/', views.login, name = 'login'),
    path('recuperar/', views.solicitar_recuperacion, name='solicitar_recuperacion'),
    path('recuperar/<str:token>/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('usuarios/seguir-autor-por-video/<int:video_id>/', views.SeguirPorVideo.as_view(), name='SeguirPorVideo'),
]
