/**
 * inventario.js - Funciones JavaScript para el módulo de inventario
 */

// Funciones para gestión de productos
function actualizarStockProducto(productoId, cantidad) {
    // Código para actualizar el stock
    console.log(`Actualizando stock del producto ${productoId} a ${cantidad}`);
}

// Inicialización de componentes y datepickers
document.addEventListener('DOMContentLoaded', function() {
    // Si hay datepickers en la página, inicializarlos
    if (typeof $.fn.datepicker !== 'undefined') {
        $('.datepicker').datepicker({
            format: 'dd/mm/yyyy',
            autoclose: true,
            language: 'es'
        });
    } else {
        console.warn('jQuery UI Datepicker no está disponible');
    }
    
    // Inicialización de tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Exportar funciones para uso global
window.inventarioApp = {
    actualizarStockProducto: actualizarStockProducto
}; 