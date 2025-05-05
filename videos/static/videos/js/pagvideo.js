document.addEventListener('DOMContentLoaded', function () {
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
    const res = await fetch("/videos");
    const json = await res.json();
    const videos = json.videos;

    const container = document.querySelector(".recommended-videos");

    for (const video of videos) {

      const item = document.createElement("div");
      item.classList.add("recommended-item");
    
      // Creamos el HTML del bloque de etiquetas como <span>
      const etiquetasHTML = video.etiquetas.map(etiqueta => `
        <span class="etiqueta">${etiqueta}</span>
      `).join('');
    
      item.innerHTML = `
        <div class="thumbnail">
          <img src="${video.miniatura}" alt="Video recomendado">
          <span class="duration">12:45</span>
        </div>
        <div class="video-details">
          <h3>${video.titulo}</h3>
          <div class="etiquetas">${etiquetasHTML}</div>
          <p>${video.canal}</p>
        </div>
      `;
    
      item.addEventListener("click", () => {
        window.location.href = `/videos/ver/${video.id_video}`;
      });
    
      container.appendChild(item);
      
    }
    
  } catch (error) {
    console.error("Error al cargar videos:", error);
  }
}
