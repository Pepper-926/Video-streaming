#Modulo de python para manejar la nube
import boto3
from django.conf import settings
import subprocess
import os
from PIL import Image
from io import BytesIO
import base64

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
    ruta_local_stream = os.path.join(settings.MEDIA_ROOT, 'stream', str(video_id))
    archivos_stream = os.listdir(ruta_local_stream)

    s3 = boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    urls_firmadas = []

    # ➡️ 1. Firmar todos los fragmentos HLS
    for archivo in archivos_stream:
        nombre_s3 = f"videos/video{video_id}/{archivo}"
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

    # ➡️ 2. Firmar la miniatura (si existe)
    nombre_miniatura_local = os.path.join(settings.MEDIA_ROOT, 'videos', f'video{video_id}', 'miniatura.jpg')

    if os.path.exists(nombre_miniatura_local):
        nombre_miniatura_s3 = f"videos/video{video_id}/miniatura.jpg"
        url_miniatura = s3.generate_presigned_url(
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
    else:
        # Miniatura no existe → simplemente no hacemos nada, no fallamos.
        pass

    return urls_firmadas

def optimizar_imagen(imagen_file, calidad=70, formato_salida='JPEG', resize_minimo=(400, 225)):
    """
    Optimiza una imagen recibida (InMemoryUploadedFile).
    
    - calidad: Calidad JPEG (1-100).
    - formato_salida: 'JPEG', 'PNG', etc.
    - resize_minimo: (ancho, alto) mínimo. Si la imagen es más grande, no cambia tamaño.
    
    Retorna:
    - base64_string: imagen codificada en base64 lista para mandar al frontend.
    """
    img = Image.open(imagen_file)

    # Asegurar que sea modo RGB para JPEG (evita error de conversión)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # (opcional) Redimensionar si es más pequeño que el mínimo
    if img.width < resize_minimo[0] or img.height < resize_minimo[1]:
        img = img.resize(resize_minimo)

    # Guardar en memoria
    buffer = BytesIO()
    img.save(buffer, format=formato_salida, quality=calidad, optimize=True)
    buffer.seek(0)

    # Codificar a base64
    base64_string = base64.b64encode(buffer.read()).decode('utf-8')
    return base64_string