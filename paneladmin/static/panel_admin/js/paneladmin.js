document.addEventListener('DOMContentLoaded', function () {
  setupTabSwitching(); // Asegúrate de que se ejecute esta función al cargar la página
});

function setupTabSwitching() {
  document.querySelectorAll('.admin-sidebar a').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const tabId = link.getAttribute('data-tab');
      
      // Eliminar las clases 'active' de todos los enlaces y secciones
      document.querySelectorAll('.admin-sidebar a').forEach(item => item.classList.remove('active'));
      document.querySelectorAll('.admin-section').forEach(section => section.classList.remove('active'));
      
      // Añadir 'active' al enlace y la sección seleccionados
      link.classList.add('active');
      document.getElementById(tabId).classList.add('active');

       if (tabId === 'users') {
        currentPage = 1;
        const usuariosContainer = document.getElementById('usuarios-body');
        usuariosContainer.innerHTML = ''; // Limpiar el contenedor de usuarios
        cargarUsuarios();
      }
    });
  });
}
