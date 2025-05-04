# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone

class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=16)
    a_pat = models.CharField(max_length=16, blank=True, null=True)
    a_mat = models.CharField(max_length=16, blank=True, null=True)
    nacimiento = models.DateField()
    correo = models.CharField(unique=True, max_length=50)
    contra = models.CharField(max_length=64)
    foto_perfil = models.CharField(max_length=64, blank=True, null=True)
    id_rol = models.ForeignKey('Roles', models.DO_NOTHING, db_column='id_rol')

    class Meta:
        managed = False
        db_table = 'usuarios'


class Roles(models.Model):
    id_rol = models.AutoField(primary_key=True)
    rol = models.CharField(unique=True, max_length=10)

    class Meta:
        managed = False
        db_table = 'roles'

class Canales(models.Model):
    id_canal = models.AutoField(primary_key=True)
    nombre_canal = models.CharField(unique=True, max_length=30)
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario')

    class Meta:
        managed = False
        db_table = 'canales'

class PasswordResetToken(models.Model):
    id_usuario = models.ForeignKey(Usuarios, on_delete=models.CASCADE)  # Relacionado con el modelo de usuario
    token = models.CharField(max_length=255)  # El token de recuperación
    created_at = models.DateTimeField(default=timezone.now)  # Fecha de creación del token
    is_used = models.BooleanField(default=False)  # Indica si el token ya fue utilizado

    class Meta:
        managed = False
        db_table = 'canales'