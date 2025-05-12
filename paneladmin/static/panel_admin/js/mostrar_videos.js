let videoIndex = 0;

document.addEventListener('DOMContentLoaded', function () {
  cargarVideos(); // Inicia mostrando el primer video
});

let videosData = []; // Guardamos los datos localmente

async function cargarVideos() {
  try {
    const res = await fetch('/videos/?revisado=False');
    const data = await res.json();

    videosData = data.videos || [];
    mostrarVideoActual();
  } catch (error) {
    console.error("Error al cargar los videos:", error);
  }
}

function mostrarVideoActual() {
  const videosContainer = document.getElementById('videos-list');
  videosContainer.innerHTML = '';

  if (videoIndex >= videosData.length) {
    videosContainer.innerHTML = '<p>Todos los videos han sido revisados.</p>';
    return;
  }

  const video = videosData[videoIndex];

  const videoElement = document.createElement('div');
  videoElement.classList.add('admin-card');

  videoElement.innerHTML = `
    <div class="video-player">
      <div class="video-container">
        <video id="video-player-${video.id_video}" controls poster="${video.miniatura || ''}">
          Tu navegador no soporta video HTML5.
        </video>
      </div>
    </div>
    <div class="video-info">
      <h3>${video.titulo}</h3>
      <p>Subido por: <strong>@${video.canal}</strong></p>
      <p>Fecha: ${new Date().toLocaleDateString()}</p>
    </div>
    <div class="admin-actions">
      <button class="approve-btn" onclick="aprobarVideo(${video.id_video})">Aprobar</button>
      <button class="reject-btn" onclick="rechazarVideo(${video.id_video})">Rechazar</button>
    </div>
  `;

  videosContainer.appendChild(videoElement);
  cargarVideoEnReproductor(video.id_video);
}

function aprobarVideo(videoId) {
  fetch(`/videos/approve/${videoId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),  // Asegúrate de obtener el CSRF token si es necesario
    },
    body: JSON.stringify({ 'status': 'approved' })
  })
  .then(response => {
    if (response.ok) {
      alert('Video aprobado');
      videoIndex++;
      mostrarVideoActual();
      //cargarVideos();  // Recargar videos después de la aprobación
    }
  })
  .catch(error => {
    console.error('Error al aprobar el video:', error);
  });
}

function rechazarVideo(videoId) {
  fetch(`/videos/${videoId}`, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),  // Asegúrate de obtener el CSRF token si es necesario
    }
  })
  .then(response => {
    if (response.ok) {
      alert('Video rechazado');
      videoIndex++;
      mostrarVideoActual();
      //cargarVideos();  // Recargar videos después de rechazar
    }
  })
  .catch(error => {
    console.error('Error al rechazar el video:', error);
  });
}

// Función para obtener el token CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Función que carga el video en el reproductor
function cargarVideoEnReproductor(videoId) {
  const video = document.getElementById(`video-player-${videoId}`);

  // Realizar la petición para obtener el archivo .m3u8
  fetch(`/videos/stream/${videoId}/`)  // Esto hace el fetch para obtener el archivo m3u8
      .then(res => res.text())
      .then(m3u8Content => {
          const blob = new Blob([m3u8Content], { type: 'application/vnd.apple.mpegurl' });
          const url = URL.createObjectURL(blob);

          // Si el navegador soporta HLS.js
          if (Hls.isSupported()) {
              const hls = new Hls();
              hls.loadSource(url);  // Cargar el archivo .m3u8
              hls.attachMedia(video);  // Asociar el video con el reproductor
          } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
              // Si el navegador soporta HLS nativamente (como Safari)
              video.src = url;
          } else {
              console.error("HLS no soportado en este navegador.");
          }
      })
      .catch(error => {
          console.error("Error al cargar el video:", error);
      });
}
