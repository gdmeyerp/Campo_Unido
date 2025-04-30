// Inicialización de componentes del foro
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    try {
        if (typeof $ !== 'undefined' && typeof $.fn.tooltip !== 'undefined') {
            $('[data-toggle="tooltip"]').tooltip();
            console.log('Tooltips inicializados con jQuery');
        } else {
            console.warn('jQuery o Bootstrap tooltip no están disponibles');
        }
    } catch (e) {
        console.error('Error al inicializar tooltips:', e);
    }
    
    // Inicializar dropdowns de Bootstrap
    try {
        if (typeof $ !== 'undefined' && typeof $.fn.dropdown !== 'undefined') {
            $('.dropdown-toggle').dropdown();
            console.log('Dropdowns inicializados con jQuery');
        } else {
            console.warn('jQuery o Bootstrap dropdown no están disponibles');
        }
    } catch (e) {
        console.error('Error al inicializar dropdowns:', e);
    }
    
    // Manejar el formulario de búsqueda
    var searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            var searchInput = this.querySelector('input[name="q"]');
            if (!searchInput.value.trim()) {
                e.preventDefault();
                searchInput.focus();
            }
        });
    }
    
    // Añadir clases de Bootstrap a botones y inputs generados por Django
    document.querySelectorAll('input[type="submit"]').forEach(function(button) {
        if (!button.classList.contains('btn')) {
            button.classList.add('btn', 'btn-primary');
        }
    });
    
    document.querySelectorAll('input[type="text"], input[type="password"], input[type="email"], textarea').forEach(function(input) {
        if (!input.classList.contains('form-control')) {
            input.classList.add('form-control');
        }
    });
    
    document.querySelectorAll('select').forEach(function(select) {
        if (!select.classList.contains('form-control')) {
            select.classList.add('form-control');
        }
    });
    
    // Verificar si estamos en la página de administración o creación de foros
    if (window.location.href.includes('/foro/admin/') || window.location.href.includes('/foro/crear-foro/')) {
        console.log('Estamos en una página de administración de foros');
    }
}); 