document.addEventListener('DOMContentLoaded', async () => {
    const videoId = window.videoIdGlobal;  // Asegúrate de tener esta variable global
    const boton = document.getElementById('subscribe-btn');

    if (!videoId || !boton) return;

    try {
      const res = await fetch(`/usuarios/seguir-autor-por-video/${videoId}/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`, // O donde almacenes el token
        }
      });

      const data = await res.json();

      if (data.ok) {
        boton.textContent = data.siguiendo ? 'Desuscribirse' : 'Suscribirse';
      } else {
        console.error(data.message || 'Error al consultar el seguimiento');
      }

    } catch (err) {
      console.error('Error de red o del servidor:', err);
    }
  });

  async function toggleSuscripcion() {
    const boton = document.getElementById('subscribe-btn');
    const contador = document.getElementById('subscribers-count');
    const videoId = window.videoIdGlobal;

    if (!boton || !videoId || !contador) return;

    const accion = boton.textContent.trim() === 'Desuscribirse' ? 'DELETE' : 'POST';

    try {
      const res = await fetch(`/usuarios/seguir-autor-por-video/${videoId}/`, {
        method: accion,
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      const data = await res.json();

        if (res.status === 401) {
            window.location.href = '/login';
            return;
        }

      if (res.ok && data.ok) {
        // Actualizamos texto del botón
        const nuevoTexto = accion === 'POST' ? 'Desuscribirse' : 'Suscribirse';
        boton.textContent = nuevoTexto;

        // Reconsultamos número de seguidores actualizado
        const estadoRes = await fetch(`/usuarios/seguir-autor-por-video/${videoId}/`, {
          method: 'GET',
          headers: {
            'X-Requested-With': 'XMLHttpRequest'
          }
        });

        const estadoData = await estadoRes.json();

        if (estadoRes.ok && estadoData.ok && typeof estadoData.seguidores === 'number') {
          contador.textContent = estadoData.seguidores;
        }
      } else {
        console.error('Error en la acción:', data.message);
      }

    } catch (err) {
      console.error('Error en la solicitud:', err);
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