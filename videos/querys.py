from django.db import connection #se usa para las tablas donde hay claves agrupadas ya que django no lo maneja

#Insert para poder insertar en donde hay claves primarias agrupadas
def asociar_etiquetas(video, etiquetas):
    with connection.cursor() as cursor:
        for etiqueta in etiquetas:
            cursor.execute(
                "INSERT INTO videos_etiquetas (id_video, id_etiqueta) VALUES (%s, %s)",
                [video.id_video, etiqueta.id_etiqueta]
            )