#Modulo de python para manejar el formateo de los videos a HLS y subirlo a la nube
import os
import subprocess
from pathlib import Path

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
