document.getElementById('form-busqueda').addEventListener('submit', async function (e) {
  e.preventDefault();

  const query = document.getElementById('busqueda').value.trim();
  const grid = document.querySelector('.video-grid');
  const mensaje = document.getElementById('search-message');

  grid.innerHTML = '<p>Buscando videos...</p>';
  mensaje.innerHTML = '';

  try {
    const response = await fetch(`/videos?titulo=${encodeURIComponent(query)}`);
    const result = await response.json();

    grid.innerHTML = '';
    mensaje.innerHTML = '';

    if (result.videos.length === 0) {
      mensaje.innerHTML = '<p>No se encontraron videos.</p>';
      return;
    }

    // Mostrar mensaje arriba del grid
    mensaje.innerHTML = `<h2>Resultados para: "<span id="search-query">${query}</span>"</h2>`;
    mensaje.innerHTML += `<button id="back-to-home" onclick="clear_search()">Limpiar</button>`;

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
    grid.innerHTML = '<p>Error al buscar videos.</p>';
    console.error(error);
  }
});

async function clear_search() {
    try {
        const response = await fetch('/videos');
        const result = await response.json();
        const mensaje = document.getElementById('search-message');

        mensaje.innerHTML = '';
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
};
