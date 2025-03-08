// Función para obtener el token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Función para añadir productos al carrito
function addToCart(productId, quantity = 1) {
    fetch('/marketplace/api/carrito/agregar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCounter(data.cart_count);
            showNotification('Producto añadido al carrito', 'success');
        } else {
            showNotification(data.error || 'Error al añadir al carrito', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error al añadir al carrito', 'error');
    });
}

// Función para añadir productos a la lista de deseos
function addToWishlist(productId) {
    fetch('/marketplace/api/lista-deseos/agregar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Producto añadido a favoritos', 'success');
        } else {
            showNotification(data.error || 'Error al añadir a favoritos', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error al añadir a favoritos', 'error');
    });
}

// Función para actualizar el contador del carrito
function updateCartCounter(count) {
    const cartCounter = document.getElementById('cart-counter');
    if (cartCounter) {
        cartCounter.textContent = count;
        cartCounter.classList.remove('d-none');
    }
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    // Aquí puedes implementar tu sistema de notificaciones preferido
    alert(message);
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Manejadores para botones de carrito
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            addToCart(productId);
        });
    });

    // Manejadores para botones de lista de deseos
    document.querySelectorAll('.add-to-wishlist').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            addToWishlist(productId);
            this.innerHTML = '<i class="fas fa-heart"></i>';
            this.classList.remove('btn-outline-secondary');
            this.classList.add('btn-danger');
        });
    });
}); 