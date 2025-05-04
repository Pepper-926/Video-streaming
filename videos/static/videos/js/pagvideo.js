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
  