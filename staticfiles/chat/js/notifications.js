// Script para manejar notificaciones para mensajes nuevos de chat

class ChatNotifications {
    constructor() {
        // Checar si el navegador soporta notificaciones
        this.notificationsSupported = 'Notification' in window;
        this.notificationsEnabled = false;
        
        // Precargar el sonido de notificación
        this.notificationSound = new Audio('/static/chat/sounds/notification.mp3');
        this.notificationSound.load();
        this.notificationSound.volume = 0.5; // 50% de volumen
        
        // Inicializar
        this.init();
    }
    
    init() {
        // Si las notificaciones no son soportadas, retornar
        if (!this.notificationsSupported) {
            console.log('Las notificaciones no son soportadas en este navegador');
            return;
        }
        
        // Verificar permisos actuales
        if (Notification.permission === 'granted') {
            this.notificationsEnabled = true;
        }
        
        // Escuchar eventos de mensajes nuevos
        this.setupEventListeners();
    }
    
    // Configurar escuchas de eventos
    setupEventListeners() {
        // Escuchar evento personalizado de mensaje nuevo
        document.addEventListener('newChatMessage', (e) => {
            const { message, roomId, isVisible } = e.detail;
            
            // Solo mostrar notificación si la ventana no está visible
            // o si el usuario no está viendo la conversación actualmente
            if (!isVisible || !this.isUserInRoom(roomId)) {
                this.showNotification(message);
            }
        });
        
        // Escuchar cambios de visibilidad para manejar notificaciones
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                // Si la página se vuelve visible, detener cualquier sonido de notificación
                this.notificationSound.pause();
                this.notificationSound.currentTime = 0;
            }
        });
    }
    
    // Verificar si el usuario está viendo la conversación actual
    isUserInRoom(roomId) {
        // Si estamos en la página de chat y la sala activa es la misma que 
        // la sala del mensaje
        const path = window.location.pathname;
        const isInChatRoom = path.includes('/chat/room/');
        
        if (!isInChatRoom) return false;
        
        // Obtener ID de sala de la URL
        const urlRoomId = path.split('/').filter(Boolean).pop();
        return urlRoomId === roomId.toString();
    }
    
    // Mostrar una notificación
    showNotification(messageData) {
        // Si no tenemos permisos, solicitarlos
        if (Notification.permission === 'default') {
            this.requestPermission().then(permission => {
                if (permission === 'granted') {
                    this.createNotification(messageData);
                }
            });
        } else if (Notification.permission === 'granted') {
            this.createNotification(messageData);
        }
    }
    
    // Solicitar permiso para notificaciones
    requestPermission() {
        return Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                this.notificationsEnabled = true;
            }
            return permission;
        });
    }
    
    // Crear y mostrar la notificación
    createNotification(messageData) {
        const { sender, content, room } = messageData;
        
        // Crear título adecuado
        const title = `Nuevo mensaje de ${sender.username || sender.email.split('@')[0]}`;
        
        // Opciones de la notificación
        const options = {
            body: content.length > 60 ? content.substring(0, 57) + '...' : content,
            icon: sender.profile_picture || '/static/images/default-avatar.png',
            badge: '/static/images/chat-badge.png',
            tag: `chat-message-${room.id}`, // Agrupa notificaciones de la misma sala
            requireInteraction: false, // No requiere interacción del usuario
            silent: false, // Reproducir sonido
            data: {
                roomId: room.id,
                url: `/chat/room/${room.id}/`,
                timestamp: new Date().getTime()
            }
        };
        
        // Crear la notificación
        const notification = new Notification(title, options);
        
        // Evento al hacer clic en la notificación
        notification.onclick = function() {
            window.focus(); // Enfocar la ventana
            // Redirigir a la sala de chat
            window.location.href = this.data.url;
            this.close();
        };
        
        // Cerrar automáticamente después de 5 segundos
        setTimeout(() => {
            notification.close();
        }, 5000);
        
        // Reproducir sonido de notificación
        this.playNotificationSound();
    }
    
    // Reproducir sonido de notificación
    playNotificationSound() {
        try {
            // Reiniciar el sonido
            this.notificationSound.currentTime = 0;
            
            // Intentar reproducir el sonido
            const playPromise = this.notificationSound.play();
            
            // Manejar la promesa de reproducción (para navegadores modernos)
            if (playPromise !== undefined) {
                playPromise.catch(error => {
                    console.warn('No se pudo reproducir el sonido de notificación:', error);
                    
                    // Crear un nuevo objeto de Audio como respaldo
                    const backupAudio = new Audio('/static/chat/sounds/notification.mp3');
                    backupAudio.volume = 0.5;
                    backupAudio.play().catch(e => {
                        console.error('Error definitivo al reproducir sonido:', e);
                    });
                });
            }
        } catch (error) {
            console.error('Error al intentar reproducir sonido de notificación:', error);
        }
    }
}

// Inicializar el manejador de notificaciones cuando el DOM está listo
document.addEventListener('DOMContentLoaded', () => {
    window.chatNotifications = new ChatNotifications();
}); 