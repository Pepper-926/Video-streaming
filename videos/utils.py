#Modulo de python para manejar la nube
import boto3
from django.conf import settings
import subprocess
import os

def convertir_a_hls(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.m3u8")

    comando = [
        "ffmpeg",
        "-i", input_path,
        "-profile:v", "baseline",
        "-level", "3.0",
        "-start_number", "0",
        "-hls_time", "10",
        "-hls_list_size", "0",
        "-f", "hls",
        output_path
    ]

    subprocess.run(comando, check=True)

def generar_urls_firmadas_para_stream(video_id):
    # Carpeta local donde están los archivos HLS
    ruta_local = os.path.join(settings.MEDIA_ROOT, 'stream', str(video_id))
    archivos = os.listdir(ruta_local)

    # Cliente S3
    s3 = boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    urls_firmadas = []

    for archivo in archivos:
        nombre_s3 = f"videos/video{video_id}/{archivo}"  # ✅ Corrige el path S3
        url = s3.generate_presigned_url(
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

    return urls_firmadas