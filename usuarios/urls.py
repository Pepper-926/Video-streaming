from django.urls import path
from . import views
from videos import views as videos_views


urlpatterns  = [
    path('', views.registrar_usuario, name = 'registrar_usuario'),
    path('login/', views.login, name = 'login'),
    path('index/', videos_views.index, name='index'),
]
