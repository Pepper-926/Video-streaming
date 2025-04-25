from django.urls import path
from . import views


urlpatterns  = [
    path('', views.registrar_usuario, name = 'registrar_usuario'),
    path('login/', views.login, name = 'login'),
    path('inicio/', views.inicio, name = 'inicio'),
]