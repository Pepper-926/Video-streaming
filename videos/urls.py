from django.urls import path
from . import views


urlpatterns  = [
    path('', views.index, name=''),
    path('videos/upload/', views.form_video, name='form_video'),
    path('videos/', views.VideosView.as_view(), name='VideosView'),
    path('videos/<int:video_id>', views.VideoDetailsViews.as_view(), name='VideoDetailsViews'),
    path('urls-s3/<int:video_id>', views.obtener_urls_s3, name='obtener_urls_s3'),
    path('videos/subida/<int:video_id>/', views.confirmar_subida, name='confirmar_subida'),
    path('videos/estado/<int:video_id>/', views.video_estado, name='video_estado'),
    path('videos/subido/<int:video_id>/', views.video_nube, name='video_nube'),
    path('videos/ver/<int:video_id>/', views.ver_video, name='ver_video'),
    path('videos/stream/<int:video_id>/', views.stream_m3u8, name='stream_m3u8'),
    path('videos/<int:video_id>/like/', views.LikesVideos.as_view(), name='LikesVideos'),
    path('videos/<int:video_id>/dislike/', views.DislikesVideos.as_view(), name='DislikesVideos')
]