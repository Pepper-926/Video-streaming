from django.db import models

'''
Modelos de vistas
'''
#Vista que devuelve las etiquetas del video buscado
class EtiquetasDeVideos(models.Model):
    id = models.AutoField(primary_key=True)
    id_video = models.IntegerField()
    publico = models.BooleanField()
    categoria = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'vw_videos_con_etiquetas'

#Vista que devuelve el canal y su foto de perfil a partir de un video
class VistaCanalDeVideo(models.Model):
    id_video = models.IntegerField(primary_key=True)
    publico = models.BooleanField()
    nombre_canal = models.CharField(max_length=30)
    foto_perfil = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'vista_canal_de_video'

'''
Modelos de tablas
'''

class Etiquetas(models.Model):
    id_etiqueta = models.AutoField(primary_key=True)
    categoria = models.CharField(unique=True, max_length=15)
    descripcion = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.categoria}: {self.descripcion}"

    class Meta:
        managed = False
        db_table = 'etiquetas'

class Videos(models.Model):
    id_video = models.AutoField(primary_key=True)
    link = models.CharField(max_length=128)
    calificacion = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    titulo = models.CharField(max_length=30)
    descripcion = models.TextField(blank=True, null=True)
    conversion_completa = models.BooleanField(default=False)
    estado = models.BooleanField(default=False)
    revisado = models.BooleanField(default=False)
    publico = models.BooleanField(default=False)
    fecha_publicado = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    miniatura = models.CharField(max_length=64, blank=True, null=True)
    id_canal = models.ForeignKey('usuarios.Canales', on_delete=models.CASCADE, db_column='id_canal')

    def __str__(self):
        return f"{self.id_video}|{self.link}|{self.calificacion}|{self.titulo}|{self.descripcion}|{self.estado}|{self.revisado}|{self.publico}|{self.fecha_publicado}|{self.miniatura}|{self.id_canal.id_canal}"

    class Meta:
        managed = False
        db_table = 'videos'


class VideosEtiquetas(models.Model):
    id_video = models.ForeignKey(Videos, on_delete=models.CASCADE, db_column='id_video')
    id_etiqueta = models.ForeignKey(Etiquetas, on_delete=models.CASCADE, db_column='id_etiqueta')

    class Meta:
        managed = False
        db_table = 'videos_etiquetas'
        unique_together = (('id_video', 'id_etiqueta'),)

class LikesDislikesVideos(models.Model):
    id_usuario = models.ForeignKey('usuarios.Usuarios', on_delete=models.CASCADE, db_column='id_usuario')
    id_video = models.ForeignKey(Videos, on_delete=models.CASCADE, db_column='id_video')
    tipo_reaccion = models.BooleanField()
    fecha_reaccion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'likes_dislikes_videos'
        unique_together = (('id_usuario', 'id_video'),)