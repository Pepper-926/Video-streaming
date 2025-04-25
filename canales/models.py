from django.db import models

class Canales(models.Model):
    id_canal = models.AutoField(primary_key=True)
    nombre_canal = models.CharField(unique=True, max_length=30)
    id_usuario = models.ForeignKey('usuarios.Usuarios', on_delete=models.CASCADE, db_column='id_usuario')

    class Meta:
        managed = False
        db_table = 'canales'
