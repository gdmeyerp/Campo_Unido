document.addEventListener('DOMContentLoaded', function() {
    console.log('Editor fix script cargado correctamente');
    
    // Función para corregir un textarea específico
    function fixTextarea(textarea) {
        console.log('Procesando textarea:', textarea.id);
        
        // 1. Eliminar estilo display:none
        if (textarea.style && textarea.style.display === 'none') {
            console.log('Quitando display:none del textarea', textarea.id);
            textarea.style.display = '';
        }
        
        // 2. Quitar el atributo required
        if (textarea.hasAttribute('required')) {
            console.log('Quitando atributo required del textarea', textarea.id);
            textarea.removeAttribute('required');
            
            // 3. Agregar validación personalizada
            var form = textarea.closest('form');
            if (form && !form._hasEditorFixListener) {
                form._hasEditorFixListener = true; // Marcar el form para evitar duplicar listeners
                
                form.addEventListener('submit', function(e) {
                    if (!textarea.value.trim()) {
                        e.preventDefault();
                        console.log('Formulario detenido - contenido vacío');
                        alert('El contenido del mensaje es obligatorio.');
                        textarea.focus();
                        // Asegurar que el textarea sea visible
                        textarea.style.display = '';
                        return false;
                    }
                    console.log('Formulario enviando - contenido válido');
                    return true;
                });
                
                console.log('Añadida validación personalizada al formulario');
            }
        }
        
        // 4. Si hay un editor EasyMDE inicializado, lo reiniciamos
        if (textarea.nextElementSibling && 
            textarea.nextElementSibling.classList.contains('EasyMDEContainer')) {
            console.log('Encontrado un contenedor EasyMDE, reiniciándolo');
            textarea.nextElementSibling.remove();
            
            // Opcional: recrear el editor si es necesario
            // Esto lo podemos añadir si queremos mantener la funcionalidad del editor
        }
    }

    // Buscar el textarea específico por ID primero
    var contentTextarea = document.getElementById('id_content');
    if (contentTextarea) {
        console.log('Textarea encontrado por ID');
        fixTextarea(contentTextarea);
    }
    
    // También buscar todos los textareas con clase machina-mde-markdown para mayor seguridad
    var textareas = document.querySelectorAll('textarea.machina-mde-markdown');
    console.log('Encontrados', textareas.length, 'textareas con clase machina-mde-markdown');
    
    textareas.forEach(function(textarea) {
        fixTextarea(textarea);
    });
    
    // Solución adicional: comprobar después de un pequeño retardo
    // Por si el editor se inicializa después de que nuestro script se ejecuta
    setTimeout(function() {
        console.log('Ejecutando revisión retardada');
        
        // Buscar nuevamente el textarea específico
        var delayedContentTextarea = document.getElementById('id_content');
        if (delayedContentTextarea) {
            fixTextarea(delayedContentTextarea);
            
            // Enfocarse en el textarea para asegurar su visibilidad
            delayedContentTextarea.focus();
            delayedContentTextarea.blur();
        }
        
        // También comprobar nuevamente todos los textareas con clase machina-mde-markdown
        var delayedTextareas = document.querySelectorAll('textarea.machina-mde-markdown');
        delayedTextareas.forEach(function(textarea) {
            fixTextarea(textarea);
        });
    }, 500);
}); 