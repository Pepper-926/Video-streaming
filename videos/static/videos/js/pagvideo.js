document.addEventListener('DOMContentLoaded', function () {
    cargar_reacciones();
    const video = document.getElementById('video-player');
    const videoId = window.videoIdGlobal;
  
    fetch(`/videos/stream/${videoId}/`)
      .then(res => res.text())
      .then(m3u8Content => {
        const blob = new Blob([m3u8Content], { type: 'application/vnd.apple.mpegurl' });
        const url = URL.createObjectURL(blob);

        if (Hls.isSupported()) {
          const hls = new Hls();
          hls.loadSource(url);
          hls.attachMedia(video);
        } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
          video.src = url;
        } else {
          console.error("HLS no soportado en este navegador.");
        }
      })
      .catch(error => {
        console.error("Error al cargar el video:", error);
      });
  });
  
async function load_videos() {
  try {
    const videoId = window.videoIdGlobal;
    const res = await fetch("/videos");
    const json = await res.json();
    const videos = json.videos;

    const container = document.querySelector(".recommended-videos");

    for (const video of videos) {
      if (video.id_video != videoId) {
        const item = document.createElement("div");
        item.classList.add("recommended-item");
      
        // 1. Tomamos las primeras 5 etiquetas
        const etiquetasVisibles = video.etiquetas.slice(0, 5).map(etiqueta => `
          <span class="etiqueta">${etiqueta}</span>
        `).join('');

        let extra = '';
        if (video.etiquetas.length > 5) {
          const etiquetasOcultas = video.etiquetas.slice(5).join(', ');
          extra = `
            <span class="etiqueta etiqueta-tooltip">
              ...
              <div class="tooltip">${etiquetasOcultas}</div>
            </span>
          `;
        }
        
        item.innerHTML = `
          <div class="thumbnail">
            <img src="${video.miniatura}" alt="Video recomendado">
            <span class="duration"></span>
          </div>
          <div class="video-details">
            <h3>${video.titulo}</h3>
            <div class="etiquetas">${etiquetasVisibles + extra}</div>
            <p>${video.canal}</p>
          </div>
        `;

        item.addEventListener("click", () => {
          window.location.href = `/videos/ver/${video.id_video}`;
        });
      
        container.appendChild(item);
        }
    }
    
  } catch (error) {
    console.error("Error al cargar videos:", error);
  }
}

async function dar_like() {
  try {
    const videoId = window.videoIdGlobal;
    const likeButton = document.getElementById('like-img');
    const dislikeButton = document.getElementById('dislike-img');

    const res = await fetch(`/videos/${videoId}/like/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest', // Esto lo detectará el decorador
      },
    });

    if (res.status === 401) {
      const data = await res.json();
      if (data.redirect) window.location.href = "/login";
      return;
    }

    const data = await res.json();

    if (data.ok) {
      likeButton.src = data.liked
        ? "/static/videos/img/like-on.svg"
        : "/static/videos/img/like-off.svg";

      if (data.liked) {
        dislikeButton.src = "/static/videos/img/dislike-off.svg";
      }

      document.getElementById('like-count').innerText = data.likes;
      document.getElementById('dislike-count').innerText = data.dislikes;
    }

  } catch (error) {
    console.error(error);
    alert('Error al dar like.' + error);
  }
}

async function dar_dislike() {
  try {
    const videoId = window.videoIdGlobal;
    const dislikeButton = document.getElementById('dislike-img');
    const likeButton = document.getElementById('like-img');

    const res = await fetch(`/videos/${videoId}/dislike/`, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
      },
    });

    if (res.status === 401) {
      const data = await res.json();
      if (data.redirect) {
        window.location.href = "/login";
        return;
      }
    }

    const data = await res.json();

    if (data.ok) {
      // Actualiza botón de dislike
      dislikeButton.src = data.disliked
        ? "/static/videos/img/dislike-on.svg"
        : "/static/videos/img/dislike-off.svg";

      // Si se dio dislike, desactiva like si estaba activo
      if (data.disliked) {
        likeButton.src = "/static/videos/img/like-off.svg";
      }

      // Actualiza contadores
      const likeCount = document.getElementById('like-count');
      const dislikeCount = document.getElementById('dislike-count');
      if (likeCount) likeCount.innerText = data.likes;
      if (dislikeCount) dislikeCount.innerText = data.dislikes;
    }

  } catch (error) {
    console.error(error);
    alert('Parece que hubo un error al dar dislike. ' + error);
  }
}


function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function copiar_link() {
  const urlActual = window.location.href;

  navigator.clipboard.writeText(urlActual)
    .then(() => {
      alert('¡Enlace copiado al portapapeles!');
    })
    .catch(err => {
      console.error('Error al copiar el enlace:', err);
      alert('No se pudo copiar el enlace.');
    });
}

async function cargar_reacciones() {
  try {
    const videoId = window.videoIdGlobal;

    const [resLike, resDislike] = await Promise.all([
      fetch(`/videos/${videoId}/like/`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      }),
      fetch(`/videos/${videoId}/dislike/`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
    ]);

    const dataLike = await resLike.json();
    const dataDislike = await resDislike.json();

    // Actualizar imagen de like
    const likeImg = document.getElementById('like-img');
    if (dataLike.liked) {
      likeImg.src = "/static/videos/img/like-on.svg";
    } else {
      likeImg.src = "/static/videos/img/like-off.svg";
    }

    /* Actualizar número de likes
    const likeCount = document.getElementById('like-count');
    if (likeCount) {
      likeCount.innerText = dataLike.likes ?? 0;
    }
    */
    // Actualizar imagen de dislike
    const dislikeImg = document.getElementById('dislike-img');
    if (dataDislike.disliked) {
      dislikeImg.src = "/static/videos/img/dislike-on.svg";
    } else {
      dislikeImg.src = "/static/videos/img/dislike-off.svg";
    }

    /* Actualizar número de dislikes
    const dislikeCount = document.getElementById('dislike-count');
    if (dislikeCount) {
      dislikeCount.innerText = dataDislike.dislikes ?? 0;
    }
      */

  } catch (error) {
    console.error("Error al cargar reacciones:", error);
  }
}
