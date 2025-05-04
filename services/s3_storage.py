import boto3
import os
import tempfile
from django.conf import settings

class S3Manager:
    def __init__(self):
        self.s3 = boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )
    
    def generar_urls_firmadas_para_stream(self, video_id):
        """
        Metodo usado para /videos 'POST'
        
        Genera una url por cada fragmento de video + su arhivo index.m3u8 + la miniatura
        
        """
        ruta_local_stream = os.path.join(settings.MEDIA_ROOT, 'stream', str(video_id))
        archivos_stream = os.listdir(ruta_local_stream)
        urls_firmadas = []

        for archivo in archivos_stream:
            nombre_s3 = f"videos/video{video_id}/{archivo}"
            url = self.s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': nombre_s3,
                'ContentType': 'application/octet-stream'
            },
            ExpiresIn=3600
            )
            urls_firmadas.append({
                'nombre_archivo': archivo,
                's3_key': nombre_s3,
                'url_firmada': url
            })

        nombre_miniatura_local = os.path.join(settings.MEDIA_ROOT, 'videos', f'video{video_id}', 'miniatura.jpg')

        if os.path.exists(nombre_miniatura_local):
            nombre_miniatura_s3 = f"videos/video{video_id}/miniatura.jpg"
            url_miniatura = self.s3.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': nombre_miniatura_s3,
                    'ContentType': 'image/jpeg'
                },
                ExpiresIn=3600
            )
            urls_firmadas.append({
                'nombre_archivo': 'miniatura.jpg',
                's3_key': nombre_miniatura_s3,
                'url_firmada': url_miniatura
            })

        return urls_firmadas
    
    def get_object(self, ruta_s3, content_type='application/octet-stream', expires_in=3600):
        """
        Genera una URL firmada para descargar un objeto de S3.

        Args:
            ruta_s3 (str): La ruta del objeto en el bucket (key).
            content_type (str): Tipo de contenido esperado. Default: 'application/octet-stream'.
            expires_in (int): Tiempo de expiración en segundos. Default: 3600 (1 hora).

        Returns:
            str: URL firmada para descarga.
        """
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': ruta_s3,
                'ResponseContentType': content_type
            },
            ExpiresIn=expires_in
        )
        return url
    
    def delete_object(self, ruta_s3, content_type='application/octet-stream', expires_in=3600):
        """
        Elimina un objeto del bucket S3.

        Args:
            ruta_s3 (str): Ruta del objeto a eliminar (key).
        
        Returns:
            dict: Respuesta de AWS S3 al intento de eliminación.
        """
        try:
            response = self.s3.delete_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=ruta_s3
            )
            return response
        except Exception as e:
            return e
        
    def delete_folder(self, prefix):
        """
        Elimina todos los objetos que tengan un prefijo (simula eliminar una carpeta).

        Args:
            prefix (str): Prefijo que representa la "carpeta" a eliminar (ej. 'videos/video56/').
        
        Returns:
            dict: Resultado de la operación de eliminación.
        """
        try:
            # Listar objetos bajo el prefijo
            response = self.s3.list_objects_v2(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Prefix=prefix
            )
            
            # Si no hay objetos, salir
            if 'Contents' not in response:
                return {'message': 'No se encontraron objetos para eliminar.'}
            
            # Crear lista de objetos a eliminar
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]

            # Eliminar objetos (máx 1000 por llamada)
            delete_response = self.s3.delete_objects(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Delete={'Objects': objects_to_delete}
            )
            return delete_response
        except Exception as e:
            raise
    
    def post_object(self, key, content_type='application/octet-stream', expires_in=3600):
        """
        Genera una URL firmada para subir un archivo a S3 usando POST.

        Args:
            key (str): La clave (ruta) del objeto en S3.
            content_type (str): Tipo de contenido del archivo.
            expires_in (int): Tiempo de expiración del formulario en segundos.

        Returns:
            dict: Diccionario con la URL y campos necesarios para subir mediante POST.
        """
        try:
            post = self.s3.generate_presigned_post(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=key,
                Fields={"Content-Type": content_type},
                Conditions=[
                    {"Content-Type": content_type}
                ],
                ExpiresIn=expires_in
            )
            return post
        except Exception as e:
            raise Exception(f"Error generando URL POST: {str(e)}")
        
    def generar_m3u8_con_urls_firmadas(self, ruta_index_m3u8, expires_in=3600):
        """
        Descarga el archivo index.m3u8 desde S3, genera URLs firmadas para los .ts,
        reemplaza las líneas y devuelve el contenido modificado como texto.

        Args:
            ruta_index_m3u8 (str): Ruta completa al index.m3u8 en S3 (ej. videos/video69/index.m3u8)
            expires_in (int): Duración de las URLs firmadas en segundos.

        Returns:
            str: Contenido del m3u8 con URLs firmadas.
        """

        try:
            # 1. Descargar el archivo index.m3u8 de S3 a un archivo temporal
            with tempfile.NamedTemporaryFile(mode='w+b', delete=False) as temp_file:
                self.s3.download_fileobj(
                    Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                    Key=ruta_index_m3u8,
                    Fileobj=temp_file
                )
                temp_file.seek(0)
                lines = temp_file.read().decode('utf-8').splitlines()

            # 2. Firmar las líneas que hacen referencia a .ts
            carpeta = ruta_index_m3u8.rsplit('/', 1)[0]
            nuevas_lineas = []
            for line in lines:
                if line.endswith('.ts'):
                    key = f"{carpeta}/{line}"
                    url = self.get_object(key, content_type='video/MP2T', expires_in=expires_in)
                    nuevas_lineas.append(url)
                else:
                    nuevas_lineas.append(line)

            return "\n".join(nuevas_lineas)

        except Exception as e:
            raise Exception(f"Error procesando index.m3u8: {str(e)}")
