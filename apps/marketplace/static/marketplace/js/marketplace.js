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
            showNotification('¡Añadido al carrito! Producto agregado correctamente', 'success');
        } else {
            showNotification(data.error || 'No se pudo agregar el producto al carrito', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('No se pudo agregar el producto al carrito', 'error');
    });
}

// Función para actualizar la cantidad en el carrito
function updateCartQuantity(itemId, quantity) {
    fetch('/marketplace/api/carrito/actualizar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Actualizar el subtotal del item
            const subtotalElement = document.querySelector(`#subtotal-${itemId}`);
            if (subtotalElement) {
                subtotalElement.textContent = `$${data.subtotal}`;
            }
            // Actualizar el total del carrito
            const totalElement = document.querySelector('#cart-total');
            if (totalElement) {
                totalElement.textContent = `$${data.total}`;
            }
            updateCartCounter(data.cart_count);
            showNotification('¡Cantidad actualizada! El carrito se ha actualizado correctamente', 'success');
        } else {
            showNotification(data.error || 'No se pudo actualizar la cantidad', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('No se pudo actualizar la cantidad', 'error');
    });
}

// Función para eliminar item del carrito
function removeFromCart(itemId) {
    fetch(`/marketplace/api/carrito/eliminar/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const itemElement = document.querySelector(`#cart-item-${itemId}`);
            if (itemElement) {
                itemElement.remove();
            }
            updateCartCounter(data.cart_count);
            showNotification('¡Producto eliminado! Se ha quitado del carrito correctamente', 'success');
            
            // Si el carrito está vacío, recargar la página
            if (data.cart_count === 0) {
                location.reload();
            } else {
                // Actualizar el total
                const totalElement = document.querySelector('#cart-total');
                if (totalElement) {
                    totalElement.textContent = `$${data.total}`;
                }
            }
        } else {
            showNotification(data.error || 'No se pudo eliminar el producto del carrito', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('No se pudo eliminar el producto del carrito', 'error');
    });
}

// Función para añadir productos a la lista de deseos
function addToWishlist(productId) {
    fetch('/marketplace/api/lista-deseos/toggle/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: `producto_id=${productId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            const wishlistBtn = document.querySelector(`.add-to-wishlist[data-product-id="${productId}"]`);
            if (wishlistBtn) {
                if (data.added) {
                    wishlistBtn.innerHTML = '<i class="fas fa-heart"></i>';
                    wishlistBtn.classList.remove('btn-outline-danger');
                    wishlistBtn.classList.add('btn-danger');
                } else {
                    wishlistBtn.innerHTML = '<i class="far fa-heart"></i>';
                    wishlistBtn.classList.remove('btn-danger');
                    wishlistBtn.classList.add('btn-outline-danger');
                }
            }
            showNotification(data.message, 'success');
        } else {
            showNotification(data.message || 'Error al actualizar favoritos', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error al actualizar favoritos', 'error');
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
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    toast.addEventListener('hidden.bs.toast', function () {
        toast.remove();
    });
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Manejadores para botones de carrito
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const quantity = document.querySelector(`#quantity-${productId}`)?.value || 1;
            addToCart(productId, parseInt(quantity));
        });
    });

    // Manejadores para botones de lista de deseos
    document.querySelectorAll('.add-to-wishlist').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            addToWishlist(productId);
        });
    });

    // Manejadores para actualización de cantidad en el carrito
    document.querySelectorAll('[data-action]').forEach(btn => {
        btn.addEventListener('click', function() {
            const container = this.closest('.quantity-control');
            const input = container.querySelector('input');
            const itemId = input.getAttribute('data-item-id');
            const action = this.getAttribute('data-action');
            let value = parseInt(input.value);
            
            if (action === 'increase') {
                value++;
            } else if (action === 'decrease' && value > 1) {
                value--;
            }
            
            input.value = value;
            updateCartQuantity(itemId, value);
        });
    });

    // Manejadores para eliminar items del carrito
    document.querySelectorAll('.delete-item-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const itemId = this.getAttribute('data-item-id');
            const card = this.closest('.cart-item');
            
            card.style.transition = 'all 0.5s ease';
            card.style.transform = 'translateX(50px)';
            card.style.opacity = '0';
            
            setTimeout(() => {
                removeFromCart(itemId);
            }, 500);
        });
    });
}); 