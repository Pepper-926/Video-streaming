document.addEventListener('DOMContentLoaded', () => {
    cargarComentarios(window.videoIdGlobal);
    const form = document.getElementById('comentario-form');
  
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
  
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());
  
      try {
        const response = await fetch('/comentarios/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data)
        });
  
        if (response.status === 401) {
          window.location.href = '/login';
          return;
        }
  
        if (response.ok) {
          const nuevoComentario = await response.json();
          console.log("Comentario recibido:", nuevoComentario);
          form.reset();
          cargarComentarios(window.videoIdGlobal);  //Esto para que se muestre el comentario recien agregado.
        } else {
          const errorData = await response.json();
          alert("Error al enviar el comentario: " + (errorData.error || "Desconocido"));
        }
  
      } catch (error) {
        console.error("Error de red:", error);
      }
    });
  });
  
  async function cargarComentarios(videoId) {
    try {
      const response = await fetch(`/comentarios?video_id=${videoId}`);
      const data = await response.json();
  
      if (!response.ok) {
        console.error("Error al obtener comentarios:", data.error);
        return;
      }
  
      const commentsContainer = document.getElementById("comments-list");
      commentsContainer.innerHTML = ""; // Limpiar antes de cargar
  
      if (data.comentarios.length === 0) {
        commentsContainer.innerHTML = "<p>¡Sé el primero en comentar!</p>";
        return;
      }
  
      data.comentarios.forEach(c => {
        const commentHtml = `
          <div class="comment">
            <img src="${c.foto_perfil}" alt="Usuario" class="user-img">
            <div class="comment-content">
              <h3>${c.usuario} <span>${c.fecha}</span></h3>
              <p>${c.texto}</p>
              <div class="comment-actions">
                <button id="boton_responder" onclick="responder_comentario(${c.id_comentario}, ${videoId})">Responder</button>
              </div>
            </div>
          </div>`;
        commentsContainer.innerHTML += commentHtml;
      });
  
    } catch (error) {
      console.error("Error al cargar comentarios:", error);
    }
  }

  function responder_comentario(id_comentario, id_video) {
    
  }