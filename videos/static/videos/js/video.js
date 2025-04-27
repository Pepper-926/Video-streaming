function toggleModal() {
    const modal = document.getElementById("tagModal");
    const isVisible = modal.style.display === "block";
    
    if (isVisible) {
      modal.style.display = "none";
      updateSelectedTags();
    } else {
      modal.style.display = "block";
    }
  }

  function updateSelectedTags() {
    const preview = document.getElementById("selected-tags-preview");
    const selected = document.querySelectorAll('#tagModal input[type="checkbox"]:checked');
    
    preview.innerHTML = ''; // limpia
    selected.forEach((checkbox) => {
      const label = checkbox.parentElement.textContent.trim();
      const pill = document.createElement("span");
      pill.textContent = label;
      preview.appendChild(pill);
    });

    if (selected.length === 0) {
      preview.innerHTML = "<em>No hay etiquetas seleccionadas</em>";
    }
  }

  window.onclick = function(event) {
    const modal = document.getElementById("tagModal");
    if (event.target === modal) {
      modal.style.display = "none";
      updateSelectedTags();
    }
  }