from django.urls import path
from . import views


urlpatterns  = [
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('registrar/login/', views.login, name = 'login'),
    path('inicio/', views.inicio, name = 'inicio'),
]