document.addEventListener('DOMContentLoaded', function() {
    // Buscar todos los textareas con clase machina-mde-markdown
    var textareas = document.querySelectorAll('textarea.machina-mde-markdown');
    
    // Recorrer cada textarea y eliminar el atributo style="display: none;"
    textareas.forEach(function(textarea) {
        // Comprobar si el textarea está oculto
        if (textarea.style.display === 'none') {
            // Eliminar el atributo style para hacerlo visible
            textarea.style.display = '';
        }
        
        // Si hay un editor EasyMDE inicializado, lo destruimos
        if (textarea.nextElementSibling && textarea.nextElementSibling.classList.contains('EasyMDEContainer')) {
            textarea.nextElementSibling.remove();
        }
    });
    
    // Eliminar el atributo required si sigue causando problemas
    setTimeout(function() {
        var contentTextarea = document.getElementById('id_content');
        if (contentTextarea && contentTextarea.hasAttribute('required')) {
            // Crear un input hidden con el mismo nombre para mantener la validación del lado del servidor
            var hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'content_required';
            hiddenInput.value = 'true';
            contentTextarea.parentNode.appendChild(hiddenInput);
            
            // Agregar un validador personalizado al formulario
            var form = contentTextarea.closest('form');
            if (form) {
                form.addEventListener('submit', function(e) {
                    if (!contentTextarea.value.trim()) {
                        e.preventDefault();
                        alert('El contenido del mensaje es obligatorio.');
                        contentTextarea.focus();
                    }
                });
            }
            
            // Quitar el atributo required para evitar el error del navegador
            contentTextarea.removeAttribute('required');
        }
    }, 500);
}); 