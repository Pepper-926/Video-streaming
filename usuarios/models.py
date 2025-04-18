# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre_canal = models.CharField(max_length=20)
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
