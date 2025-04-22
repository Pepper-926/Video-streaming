from django import forms
from .models import Videos

from django import forms

class VideoUploadForm(forms.Form):
    title = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'id': 'title'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'id': 'description'}))
    file = forms.FileField(required=True, widget=forms.FileInput(attrs={'id': 'video-file', 'accept': 'video/*'}))
    thumbnail = forms.ImageField(required=False, widget=forms.FileInput(attrs={'id': 'thumbnail', 'accept': 'image/*'}))
    visibility = forms.ChoiceField(choices=[('public', 'Público'), ('private', 'Privado')], widget=forms.Select(attrs={'id': 'visibility'}))
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'id': 'tags', 'placeholder': 'ej: comedia, tutorial, gaming'}))