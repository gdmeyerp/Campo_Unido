/**
 * JavaScript para el Explorador de Base de Datos
 */
$(document).ready(function() {
    // Inicializar tooltips
    $('[data-toggle="tooltip"]').tooltip();
    
    // Inicializar popovers
    $('[data-toggle="popover"]').popover();
    
    // Limpiar búsqueda
    $('.clear-search').click(function() {
        $(this).siblings('input').val('');
        $(this).closest('form').submit();
    });
    
    // Ordenar tabla
    $('.sort-header').click(function() {
        var field = $(this).data('field');
        var currentOrder = $('#order_by').val();
        
        if (currentOrder === field) {
            // Cambiar a orden descendente
            $('#order_by').val('-' + field);
        } else if (currentOrder === '-' + field) {
            // Volver a orden por defecto (id)
            $('#order_by').val('id');
        } else {
            // Establecer orden ascendente
            $('#order_by').val(field);
        }
        
        $('#filter-form').submit();
    });
    
    // Mostrar indicador de orden actual
    var currentOrder = $('#order_by').val();
    if (currentOrder) {
        var field = currentOrder.startsWith('-') ? currentOrder.substring(1) : currentOrder;
        var direction = currentOrder.startsWith('-') ? 'desc' : 'asc';
        
        $('.sort-header[data-field="' + field + '"]').append(
            ' <i class="fas fa-sort-' + (direction === 'asc' ? 'up' : 'down') + '"></i>'
        );
    }
    
    // Inicializar datepickers
    if ($.fn.datepicker) {
        $('.datepicker').datepicker({
            format: 'yyyy-mm-dd',
            autoclose: true,
            todayHighlight: true
        });
    }
    
    // Inicializar select2
    if ($.fn.select2) {
        $('.select2').select2({
            theme: 'bootstrap4',
            placeholder: 'Seleccionar...',
            allowClear: true
        });
    }
    
    // Expandir/colapsar secciones
    $('.section-toggle').click(function() {
        var target = $(this).data('target');
        $(target).slideToggle();
        $(this).find('i').toggleClass('fa-chevron-down fa-chevron-up');
    });
    
    // Copiar al portapapeles
    $('.copy-to-clipboard').click(function() {
        var text = $(this).data('text');
        var tempInput = $('<input>');
        $('body').append(tempInput);
        tempInput.val(text).select();
        document.execCommand('copy');
        tempInput.remove();
        
        // Mostrar mensaje de éxito
        var originalText = $(this).html();
        $(this).html('<i class="fas fa-check"></i> Copiado');
        
        var button = $(this);
        setTimeout(function() {
            button.html(originalText);
        }, 2000);
    });
    
    // Filtros avanzados
    $('#advanced-filter-form').on('submit', function() {
        // Eliminar campos vacíos para no ensuciar la URL
        $(this).find('input, select').each(function() {
            if ($(this).val() === '' || $(this).val() === null) {
                $(this).prop('disabled', true);
            }
        });
    });
    
    // Confirmar acciones peligrosas
    $('.confirm-action').click(function(e) {
        if (!confirm($(this).data('confirm') || '¿Está seguro de realizar esta acción?')) {
            e.preventDefault();
        }
    });
}); 