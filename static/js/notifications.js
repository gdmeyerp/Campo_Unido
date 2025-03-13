/**
 * Funcionalidad para actualizar y gestionar el contador de notificaciones
 */
document.addEventListener('DOMContentLoaded', function() {
    // Función para actualizar el contador de notificaciones
    function actualizarContadorNotificaciones() {
        fetch('/inventario/api/notificaciones/contador/')
            .then(response => response.json())
            .then(data => {
                const contadorElement = document.getElementById('contador-notificaciones');
                if (contadorElement) {
                    // Actualizar contador
                    contadorElement.textContent = data.count;
                    
                    // Mostrar u ocultar el badge según si hay notificaciones
                    if (data.count > 0) {
                        contadorElement.classList.remove('d-none');
                    } else {
                        contadorElement.classList.add('d-none');
                    }
                }
            })
            .catch(error => console.error('Error al actualizar contador de notificaciones:', error));
    }
    
    // Actualizar el contador al cargar la página
    actualizarContadorNotificaciones();
    
    // Configurar actualización periódica (cada 5 minutos)
    setInterval(actualizarContadorNotificaciones, 5 * 60 * 1000);

    // Agregar la funcionalidad de ventana flotante para notificaciones
    const notifBell = document.querySelector('.notification-bell');
    if (notifBell) {
        // Crear la ventana flotante si no existe
        if (!document.getElementById('notificaciones-popup')) {
            const popupContainer = document.createElement('div');
            popupContainer.id = 'notificaciones-popup';
            popupContainer.className = 'notifications-popup';
            popupContainer.innerHTML = `
                <div class="notifications-header">
                    <h6 class="m-0">Notificaciones</h6>
                    <div>
                        <button class="btn btn-sm btn-outline-primary mark-all-read">
                            <i class="fas fa-check-double"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary close-popup">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="notifications-body">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                </div>
                <div class="notifications-footer">
                    <a href="/inventario/notificaciones/" class="btn btn-sm btn-primary w-100">Ver todas</a>
                </div>
            `;
            document.body.appendChild(popupContainer);

            // Estilo para la ventana flotante
            const style = document.createElement('style');
            style.textContent = `
                .notifications-popup {
                    position: fixed;
                    width: 320px;
                    max-height: 400px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                    z-index: 1050;
                    display: none;
                    flex-direction: column;
                    overflow: hidden;
                    right: 20px;
                    top: 60px;
                }
                .notifications-popup.show {
                    display: flex;
                }
                .notifications-header {
                    padding: 10px 15px;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    background-color: #f8f9fa;
                }
                .notifications-body {
                    flex: 1;
                    overflow-y: auto;
                    max-height: 300px;
                    padding: 10px 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                .notifications-body .empty-state {
                    padding: 30px 15px;
                    text-align: center;
                    color: #6c757d;
                }
                .notifications-body .notification-item {
                    padding: 10px 15px;
                    border-bottom: 1px solid #f1f1f1;
                    cursor: pointer;
                    width: 100%;
                }
                .notifications-body .notification-item:hover {
                    background-color: #f8f9fa;
                }
                .notifications-body .notification-item.unread {
                    background-color: #e8f4ff;
                }
                .notifications-footer {
                    padding: 10px 15px;
                    border-top: 1px solid #eee;
                }
                .notification-title {
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .notification-message {
                    font-size: 0.85rem;
                    color: #555;
                    margin-bottom: 5px;
                }
                .notification-time {
                    font-size: 0.75rem;
                    color: #999;
                }
                .notification-icon {
                    margin-right: 10px;
                }
                .notification-bell {
                    cursor: pointer;
                }
            `;
            document.head.appendChild(style);

            // Agregar el evento para mostrar/ocultar el popup al hacer clic en el icono de la campana
            notifBell.addEventListener('click', function(e) {
                e.preventDefault();
                const popup = document.getElementById('notificaciones-popup');
                popup.classList.toggle('show');
                
                if (popup.classList.contains('show')) {
                    cargarNotificaciones();
                }
            });

            // Cerrar el popup al hacer clic en el botón de cerrar
            document.querySelector('.close-popup').addEventListener('click', function() {
                document.getElementById('notificaciones-popup').classList.remove('show');
            });

            // Cerrar el popup al hacer clic fuera de él
            document.addEventListener('click', function(e) {
                const popup = document.getElementById('notificaciones-popup');
                const bell = document.querySelector('.notification-bell');
                
                if (popup && bell && !popup.contains(e.target) && !bell.contains(e.target)) {
                    popup.classList.remove('show');
                }
            });

            // Marcar todas como leídas
            document.querySelector('.mark-all-read').addEventListener('click', function() {
                fetch('/inventario/notificaciones/marcar-todas-leidas/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    }
                })
                .then(response => {
                    if (response.ok) {
                        cargarNotificaciones();
                        actualizarContadorNotificaciones();
                    }
                })
                .catch(error => console.error('Error al marcar como leídas:', error));
            });
        }
    }

    // Función para cargar notificaciones recientes
    function cargarNotificaciones() {
        const notificationsBody = document.querySelector('.notifications-body');
        notificationsBody.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        `;

        fetch('/inventario/api/notificaciones/recientes/')
            .then(response => response.json())
            .then(data => {
                notificationsBody.innerHTML = '';
                
                if (data.length === 0) {
                    notificationsBody.innerHTML = `
                        <div class="empty-state">
                            <i class="fas fa-bell-slash fa-2x mb-3 text-muted"></i>
                            <p>No tienes notificaciones</p>
                        </div>
                    `;
                    return;
                }
                
                data.forEach(notif => {
                    const item = document.createElement('div');
                    item.className = `notification-item ${!notif.leida ? 'unread' : ''}`;
                    
                    let icon = '';
                    if (notif.nivel === 'INFO') icon = '<i class="fas fa-info-circle text-info notification-icon"></i>';
                    else if (notif.nivel === 'WARNING') icon = '<i class="fas fa-exclamation-triangle text-warning notification-icon"></i>';
                    else if (notif.nivel === 'ERROR') icon = '<i class="fas fa-times-circle text-danger notification-icon"></i>';
                    else if (notif.nivel === 'SUCCESS') icon = '<i class="fas fa-check-circle text-success notification-icon"></i>';
                    
                    item.innerHTML = `
                        <div class="d-flex align-items-start">
                            ${icon}
                            <div>
                                <div class="notification-title">${notif.titulo}</div>
                                <div class="notification-message">${notif.mensaje.substring(0, 100)}${notif.mensaje.length > 100 ? '...' : ''}</div>
                                <div class="notification-time">${formatearFecha(notif.fecha_creacion)}</div>
                            </div>
                        </div>
                    `;
                    
                    // Marcar como leída al hacer clic
                    item.addEventListener('click', function() {
                        if (!notif.leida) {
                            marcarComoLeida(notif.id);
                        }
                        
                        if (notif.enlace) {
                            window.location.href = notif.enlace;
                        } else {
                            window.location.href = `/inventario/notificaciones/${notif.id}/`;
                        }
                    });
                    
                    notificationsBody.appendChild(item);
                });
            })
            .catch(error => {
                console.error('Error al cargar notificaciones:', error);
                notificationsBody.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-exclamation-circle fa-2x mb-3 text-danger"></i>
                        <p>Error al cargar notificaciones</p>
                    </div>
                `;
            });
    }

    // Función para marcar una notificación como leída
    function marcarComoLeida(id) {
        fetch(`/inventario/notificaciones/${id}/marcar-leida/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => {
            if (response.ok) {
                actualizarContadorNotificaciones();
            }
        })
        .catch(error => console.error('Error al marcar como leída:', error));
    }

    // Función para obtener el token CSRF
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    }

    // Función para formatear fecha
    function formatearFecha(fechaStr) {
        const fecha = new Date(fechaStr);
        const ahora = new Date();
        const diff = Math.floor((ahora - fecha) / 1000); // diferencia en segundos
        
        if (diff < 60) return 'Hace unos segundos';
        if (diff < 3600) return `Hace ${Math.floor(diff / 60)} minutos`;
        if (diff < 86400) return `Hace ${Math.floor(diff / 3600)} horas`;
        if (diff < 604800) return `Hace ${Math.floor(diff / 86400)} días`;
        
        return fecha.toLocaleDateString();
    }
}); 