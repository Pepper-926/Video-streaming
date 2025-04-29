from django.urls import path
from . import views


urlpatterns  = [
    path('', views.index, name='index'),
    path('videos/upload/', views.form_video, name='form_video'),
    path('videos/', views.VideosView.as_view(), name='VideosView'),
    path('urls-s3/<int:video_id>', views.obtener_urls_s3, name='obtener_urls_s3'),
    path('videos/subida/<int:video_id>/', views.confirmar_subida, name='confirmar_subida'),
    path('videos/estado/<int:video_id>/', views.video_estado, name='video_estado'),
    path('videos/subido/<int:video_id>/', views.video_nube, name='video_nube'),
]