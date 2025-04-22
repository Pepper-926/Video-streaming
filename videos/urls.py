from django.urls import path
from . import views


urlpatterns  = [
    path('', views.index, name='index'),
    path('videos/upload/', views.form_video, name='form_video'),
    path('videos/', views.subir_video, name='subir_video'),
]