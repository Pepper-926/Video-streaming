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
                eliminarUsuario(userId, tr);
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

function eliminarUsuario(usuarioId, tr) {
  fetch(`/eliminar_usuario_y_canal/${usuarioId}/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('Usuario eliminado exitosamente');
      tr.remove(); // Elimina la fila de la tabla directamente
    } else {
      alert('Error al eliminar el usuario: ' + data.message);
    }
  })
  .catch(error => {
    console.error('Error al eliminar el usuario:', error);
    alert('Hubo un error al intentar eliminar el usuario');
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
