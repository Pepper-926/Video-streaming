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

def strtobool(val):
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return True
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return False
    else:
        raise ValueError(f"Invalid truth value: {val}")