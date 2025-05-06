document.addEventListener('DOMContentLoaded', function() {
    // Función para inicializar EasyMDE en un textarea
    function initializeEasyMDE(textarea) {
        // Remover el atributo required temporalmente
        textarea.removeAttribute('required');
        
        // Si ya hay un editor EasyMDE inicializado, lo destruimos
        if (textarea.nextElementSibling && textarea.nextElementSibling.classList.contains('EasyMDEContainer')) {
            textarea.nextElementSibling.remove();
        }

        // Asegurarnos que el textarea sea visible inicialmente
        textarea.style.removeProperty('display');
        
        // Inicializar el nuevo editor con configuración personalizada
        var easyMDE = new EasyMDE({
            element: textarea,
            spellChecker: false,
            status: false,
            autoDownloadFontAwesome: false,
            renderingConfig: {
                singleLineBreaks: false
            },
            toolbar: [
                'bold', 'italic', 'heading',
                '|', 'quote', 'unordered-list', 'ordered-list',
                '|', 'link', 'image',
                '|', 'preview'
            ],
            initialValue: textarea.value,
            forceSync: true
        });

        // Manejar la validación del formulario
        var form = textarea.closest('form');
        if (form) {
            form.addEventListener('submit', function(e) {
                // Sincronizar el contenido del editor con el textarea
                easyMDE.codemirror.save();
                
                // Validar que haya contenido
                if (!textarea.value.trim()) {
                    e.preventDefault();
                    alert('El contenido del mensaje es obligatorio.');
                    easyMDE.codemirror.focus();
                    return false;
                }
            });
        }

        // Observar cambios en el estilo del textarea
        var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.attributeName === 'style') {
                    // Si el textarea se oculta, mostrar el editor
                    if (textarea.style.display === 'none') {
                        textarea.style.removeProperty('display');
                    }
                }
            });
        });

        observer.observe(textarea, {
            attributes: true,
            attributeFilter: ['style']
        });

        return easyMDE;
    }

    // Inicializar todos los textareas con la clase machina-mde-markdown
    document.querySelectorAll('textarea.machina-mde-markdown').forEach(function(textarea) {
        initializeEasyMDE(textarea);
    });
}); 