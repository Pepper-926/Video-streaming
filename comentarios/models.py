# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Comentarios(models.Model):
    id_comentario = models.AutoField(primary_key=True)
    texto = models.TextField()
    revisado = models.BooleanField(default=False)
    fecha_comentado = models.DateTimeField(auto_now_add=True)
    id_video = models.ForeignKey('videos.Videos', models.DO_NOTHING, db_column='id_video')
    id_usuario = models.ForeignKey('usuarios.Usuarios', models.DO_NOTHING, db_column='id_usuario')
    id_respuesta = models.ForeignKey('self', models.DO_NOTHING, db_column='id_respuesta', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comentarios'
