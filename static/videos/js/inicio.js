document.addEventListener('DOMContentLoaded', async () => {
  try {
    const response = await fetch('/videos');
    const result = await response.json();

    const grid = document.querySelector('.video-grid');
    grid.innerHTML = ''; // Limpiar contenido anterior

    result.videos.forEach(video => {
      const card = document.createElement('div');
      card.classList.add('video-card');

      const etiquetasHTML = video.etiquetas.map(etiqueta => 
        `<span class="etiqueta">${etiqueta}</span>`
      ).join(' ');

      card.innerHTML = `
        <a href="/videos/ver/${video.id_video}">
          <img src="${video.miniatura}" alt="${video.titulo}">
        </a>
        <h3>${video.titulo}</h3>
        <p>${video.canal}</p>
        <div class="etiquetas">${etiquetasHTML}</div>
      `;

      grid.appendChild(card);
    });
  } catch (error) {
    console.error('Error al cargar videos:', error);
  }
});