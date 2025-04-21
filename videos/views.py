from django.shortcuts import render, redirect
from .models import Videos, VideosEtiquetas

def index(request):
    return render(request, 'inicio.html')