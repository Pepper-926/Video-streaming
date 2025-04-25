/* subida_s3.js
   Lógica para:
   1) Esperar la conversión (polling)
   2) Obtener URLs firmadas
   3) Subir fragmentos HLS a S3
   4) Mostrar progreso y botón final */

   async function esperarConversion(videoId) {
    const ESTADO_URL = `/videos/estado/${videoId}/`;
    let listo = false;
  
    while (!listo) {
      try {
        const res = await fetch(ESTADO_URL);
        const json = await res.json();
        listo = json.conversion_completa;
  
        if (!listo) {
          document.getElementById('estado')
            .innerText = '⏳ Fragmentando video… (esperando a que termine)';
          await new Promise(r => setTimeout(r, 3000)); // 3 s
        }
      } catch (err) {
        console.error('Error consultando estado:', err);
        document.getElementById('estado')
          .innerText = '⚠️ Error consultando estado. Reintentando…';
        await new Promise(r => setTimeout(r, 3000));
      }
    }
  }
  
  /* 1️⃣  ───────── subirFragmentos ───────── */
  async function subirFragmentos(videoId, archivosFirmados, carpetaLocal) {
    const total = archivosFirmados.length;
    let subidos = 0;

    for (const archivo of archivosFirmados) {
      const filePath = `${carpetaLocal}/${archivo.nombre_archivo}`;
      const blob     = await fetch(filePath).then(r => r.blob());

      await fetch(archivo.url_firmada, {
        method : 'PUT',
        body   : blob,
        headers: { 'Content-Type': 'application/octet-stream' }
      });

      subidos++;
      document.getElementById('progreso')
        .innerText = `Subido ${subidos} / ${total} fragmentos`;
    }

    /* ←──  AÑADE ESTE await  */
    await notificarServidor(videoId);

    document.getElementById('estado')
      .innerText = '✅ Video subido correctamente a la nube.';
    window.removeEventListener('beforeunload', () => {});
    document.getElementById('finalizado').style.display = 'block';
  }

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  }
  
  export async function notificarServidor(videoId) {
    const csrftoken = getCookie('csrftoken');
  
    /* endpoint definido en urls.py ->  path('videos/subido/<int:video_id>/') */
    await fetch(`/videos/subido/${videoId}/`, {
      method : 'POST',
      headers: { 'X-CSRFToken': csrftoken },
    });
  }

  
  /* 2️⃣  ───────── obtenerYSubir ───────── */
  async function obtenerYSubir(videoId, carpetaLocal) {
    const res   = await fetch(`/urls-s3/${videoId}`);
    const datos = await res.json();           // { archivos: [...] }

    /* ←──  AÑADE ESTE await  */
    await subirFragmentos(videoId, datos.archivos, carpetaLocal);
  }
  
  /* -------- Punto de entrada principal -------- */
  export async function iniciarSubida(videoId) {
    const carpetaLocal = `/media/stream/${videoId}`;
  
    window.addEventListener('beforeunload', e => {
      e.preventDefault();
      e.returnValue = '';
    });
  
    await esperarConversion(videoId);
    await obtenerYSubir(videoId, carpetaLocal);
  }



