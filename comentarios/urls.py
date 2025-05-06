from django.urls import path
from . import views


urlpatterns  = [
    path('comentarios/', views.ViewComentarios.as_view(), name ='ViewComentarios'),
]
