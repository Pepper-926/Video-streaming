document.querySelectorAll('.approve-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('.admin-card').style.opacity = '0.5';
      btn.textContent = '✅ Aprobado';
    });
  });
  

  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      btn.closest('.comment-card').remove();
    });
  });
  
  document.querySelectorAll('.delete-user-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const userId = btn.getAttribute('data-user-id');
      
      if (confirm(`¿Eliminar al usuario ID ${userId}? Esta acción no se puede deshacer.`)) {
        btn.closest('tr').style.opacity = '0';
        setTimeout(() => {
          btn.closest('tr').remove();
          console.log(`Usuario ID ${userId} eliminado`);
        }, 300);
      }
    });
  });