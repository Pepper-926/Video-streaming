import boto3
import os
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
                'ResponseContentType': content_type  # <- Para la descarga
            },
            ExpiresIn=expires_in
        )
        return url
