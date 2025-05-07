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
  
      if (!response.ok) {      console.error("Error al obtener comentarios:", data.error);
        return;
      }
  
      const tuId = data.tu_id;
      const commentsContainer = document.getElementById("comments-list");
      commentsContainer.innerHTML = "";
  
      if (data.comentarios.length === 0) {
        commentsContainer.innerHTML = "<p>¡Sé el primero en comentar!</p>";
        return;
      }
  
      data.comentarios.forEach(c => {
        const esPropio = tuId !== null && tuId === c.id_usuario;
        console.log(tuId !== null && tuId === c.id_usuario);
        const eliminarBtn = esPropio
          ? `<button onclick="eliminarComentario(${c.id_comentario})">Eliminar</button>`
          : "";
        
        //Cargamos las respuestas de cada comentario
        let respuestasHtml = "";
          if (c.respuestas && c.respuestas.length > 0) {
            c.respuestas.forEach(r => {
              const esPropia = tuId !== null && tuId === r.id_usuario;
              const eliminarRBtn = esPropia
                ? `<button onclick="eliminarComentario(${r.id_comentario})">Eliminar</button>`
                : "";
          
              respuestasHtml += `
                <div class="respuesta">
                  <img src="${r.foto_perfil || '/static/videos/img/default-user.png'}" alt="Usuario" class="user-img respuesta-img">
                  <div class="respuesta-content">
                    <h4>${r.usuario} <span>${r.fecha}</span></h4>
                    <p>${r.texto}</p>
                    <div class="comment-actions">
                      ${eliminarRBtn}
                    </div>
                  </div>
                </div>`;
            });
          }

        const commentHtml = `
          <div class="comment">
            <img src="${c.foto_perfil || '/static/videos/img/default-user.png'}" alt="Usuario" class="user-img">
            <div class="comment-content">
              <h3>${c.usuario} <span>${c.fecha}</span></h3>
              <p>${c.texto}</p>
              <div class="comment-actions">
                <button onclick="responder_comentario(${c.id_comentario}, ${videoId})" id="reply-${c.id_comentario}">Responder</button>
                ${eliminarBtn}
              </div>
            </div>
            <div class="reply-container" id="reply-container-${c.id_comentario}">
            ${respuestasHtml}
            </div>
          </div>`;
        commentsContainer.innerHTML += commentHtml;
      });
  
    } catch (error) {
      console.error("Error al cargar comentarios:", error);
    }
  }  

  async function eliminarComentario(idComentario) {
    if (!confirm("¿Seguro que quieres eliminar este comentario?")) return;
  
    try {
      const response = await fetch(`/comentarios/?id_comentario=${idComentario}`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
        }
      });
  
      const data = await response.json();
  
      if (response.ok) {
        alert(data.message || "Comentario eliminado.");
        cargarComentarios(window.videoIdGlobal);
      } else {
        alert("Error: " + (data.error || "No se pudo eliminar el comentario."));
      }
    } catch (error) {
      console.error("Error al eliminar comentario:", error);
    }
  }
  

  function responder_comentario(id_comentario, id_video) {
    const replyBtn = document.getElementById(`reply-${id_comentario}`);
    const container = document.getElementById(`reply-container-${id_comentario}`);
  
    // Si ya está visible, cancela (toggle)
    if (container.innerHTML !== '') {
      replyBtn.innerText = 'Responder';
      container.innerHTML = '';
      return;
    }
  
    replyBtn.innerText = 'Cancelar';
  
    // HTML del formulario
    container.innerHTML = `
      <form id="reply-form-${id_comentario}" class="reply-form">
        <input type="hidden" name="id_video" value="${id_video}">
        <input type="hidden" name="id_respuesta" value="${id_comentario}">
        <input type="text" name="contenido" placeholder="Escribe tu respuesta..." required>
        <button type="submit">Enviar</button>
      </form>
    `;
  
    // Escuchar el submit del nuevo formulario
    const form = document.getElementById(`reply-form-${id_comentario}`);
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
  
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());
  
      try {
        const response = await fetch('/comentarios/', {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data)
        });
  
        if (response.status === 401) {
          window.location.href = '/login';
          return;
        }
  
        if (response.ok) {
          form.reset();
          cargarComentarios(window.videoIdGlobal); // Recargar comentarios
        } else {
          const errorData = await response.json();
          alert("Error: " + (errorData.error || "No se pudo enviar la respuesta."));
        }
  
      } catch (error) {
        console.error("Error de red:", error);
      }
    });
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