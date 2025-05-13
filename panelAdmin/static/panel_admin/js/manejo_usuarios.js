let currentPage = 1;  // Página actual, empieza con 1

// Función para cargar los usuarios
function cargarUsuarios() { 
  const usuariosContainer = document.getElementById('usuarios-body');
  fetch('/obtener_usuarios/?page=' + currentPage) // Asumiendo que en el backend recibes el parámetro page
    .then(res => res.json())
    .then(data => {
      if (data.usuarios && data.usuarios.length > 0) {
        if (usuariosContainer) {
          data.usuarios.forEach(usuario => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td>${usuario.id_usuario}</td>
              <td>${usuario.nombre}</td>
              <td>${usuario.correo}</td>
              <td>${usuario.rol}</td>
              <td>
                <select class="role-select">
                  <option value="admin" ${usuario.rol === 'admin' ? 'selected' : ''}>Administrador</option>
                  <option value="usuario" ${usuario.rol === 'usuario' ? 'selected' : ''}>Usuario</option>
                </select>
              </td>
              <td>
                <button class="delete-user-btn" data-user-id="${usuario.id_usuario}">🗑️ Eliminar</button>
              </td>
            `;
            usuariosContainer.appendChild(tr);

            tr.querySelector('.delete-user-btn').addEventListener('click', function() {
              const userId = usuario.id_usuario;  // ← tomas el ID directamente del objeto
              if (confirm(`¿Eliminar al usuario ID ${userId}? Esta acción no se puede deshacer.`)) {
                eliminarVideosUsuario(userId)
                  .then(() => {
                    eliminarUsuario(userId, tr);
                  })
                  .catch(error => {
                    console.error("Error al eliminar los videos:", error);
                  });
              }
            });


            // Añadir evento para cambiar el rol
            tr.querySelector('.role-select').addEventListener('change', function() {
              const nuevoRol = this.value;
              console.log(nuevoRol); 
              cambiarRol(usuario.id_usuario, nuevoRol);
            });

          });

          currentPage++; // Incrementar la página después de cargar los usuarios
        }
      } else {
        console.error('No se encontraron usuarios.');
      }
    })
    .catch(error => {
      console.error('Error al cargar los usuarios:', error);
    });
}


document.addEventListener('DOMContentLoaded', function () {
  // Ahora el DOM está cargado

  const loadMoreBtn = document.getElementById('load-more-btn');
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', cargarUsuarios);
  } else {
    console.error('El botón "Cargar más" no se encuentra en el DOM');
  }
});

// Función para eliminar un usuario 
/*function eliminarUsuario(usuarioId) {
  fetch(`/eliminar_usuario_y_canal/${usuarioId}/`, {  // Llamamos la URL de eliminación
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),  // Asegúrate de tener el CSRF token
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('Usuario eliminado exitosamente');
      // Aquí puedes recargar la lista de usuarios si lo deseas
      cargarUsuarios();  // Si quieres que se recargue la lista de usuarios
    } else {
      alert('Error al eliminar el usuario: ' + data.message);
    }
  })
  .catch(error => {
    console.error('Error al eliminar el usuario:', error);
    alert('Hubo un error al intentar eliminar el usuario');
  });
}*/

function eliminarUsuario(usuarioId) {
  return fetch(`/eliminar_usuario_y_canal/${usuarioId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('Usuario eliminado exitosamente');
    } else {
      alert('Error al eliminar el usuario: ' + data.message);
    }
    return data;
  })
  .catch(error => {
    console.error('Error al eliminar el usuario:', error);
    alert('Hubo un error al intentar eliminar el usuario');
    throw error;
  });
}



// Función para eliminar los videos asociados a un usuario en la nube (usando la URL de videos)
/*function eliminarVideosUsuario(usuarioId) {
  fetch(`/videos/usuario/${usuarioId}/`, {  // Aquí la URL del endpoint para eliminar videos relacionados
    method: 'DELETE',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),  // CSRF token
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('Videos eliminados de la nube');
    } else {
      console.log('Error al eliminar los videos');
    }
  })
  .catch(error => {
    console.error('Error al eliminar los videos de la nube:', error);
  });
} */

function eliminarVideosUsuario(usuarioId) {
  return fetch(`/videos/usuario/${usuarioId}/`, {
    method: 'DELETE',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('Videos eliminados de la nube');
    } else {
      console.warn('Error al eliminar los videos:', data.message);
    }
    return data; // <-- Devuelve la respuesta para que el .then siguiente la reciba
  })
  .catch(error => {
    console.error('Error al eliminar los videos de la nube:', error);
    throw error; // <-- Lanza el error para que el .catch global lo capture
  });
}



// Función para cambiar el rol de un usuario
function cambiarRol(usuarioId, nuevoRol) {
  fetch(`/usuarios/cambiar_rol/${usuarioId}/`, {  // Asegúrate de que la URL coincida
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),  // Asegúrate de que el token CSRF esté presente
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 'rol': nuevoRol })  // Enviar el nuevo rol en el cuerpo de la solicitud

  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('Rol actualizado correctamente');
    } else {
      console.error(data.message);  // Mostrar mensaje de error si algo salió mal
    }
  })
  .catch(error => {
    console.error('Error al cambiar el rol:', error);
  });
}
