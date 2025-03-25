let allSelected = false;

// Función para seleccionar o deseleccionar todas las plataformas
function toggleSeleccionarTodo(button) {
    const selectElement = document.getElementById('plataformas');
    const options = selectElement.options;
    for (let i = 0; i < options.length; i++) {
        options[i].selected = !allSelected;
    }
    allSelected = !allSelected;
    button.textContent = allSelected ? 'Deseleccionar Todo' : 'Seleccionar Todo';
}

// Función para sincronizar el estado global cuando el usuario interactúa manualmente
function syncSelectionState() {
    const selectElement = document.getElementById('plataformas');
    const options = selectElement.options;
    allSelected = Array.from(options).every(option => option.selected);
    const toggleButton = document.querySelector('button[onclick="toggleSeleccionarTodo(this)"]');
    toggleButton.textContent = allSelected ? 'Deseleccionar Todo' : 'Seleccionar Todo';
}

// Función para mostrar el modal
function showModal() {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.style.display = 'block'; // Mostrar el modal
    } else {
        console.error('No se encontró el modal con el ID "modal".');
    }
}

// Función para cerrar el modal
function closeModal() {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.style.display = 'none'; // Ocultar el modal
    } else {
        console.error('No se encontró el modal con el ID "modal".');
    }
}

// Agregar el evento `change` al <select> para detectar cambios manuales
document.addEventListener('DOMContentLoaded', () => {
    const selectElement = document.getElementById('plataformas');
    if (selectElement) {
        selectElement.addEventListener('change', syncSelectionState);
    } else {
        console.error('No se encontró el elemento <select> con el ID "plataformas".');
    }

    // Agregar evento para cerrar el modal al hacer clic fuera de él
    const modal = document.getElementById('modal');
    if (modal) {
        window.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal();
            }
        });
    }
});
