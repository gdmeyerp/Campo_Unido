/**
 * Campo Unido - Sistema de Chat Unificado
 * Este archivo contiene la lógica compartida entre el chat flotante y el chat del dashboard
 */

// Namespace para el sistema de chat
window.CampoUnidoChat = (function() {
    // Variables globales
    let activeChats = {};
    let chatWindows = {};
    let chatUpdateIntervals = {};
    let totalUnreadCount = 0;
    
    // Opciones de configuración
    const config = {
        updateInterval: 5000,
        maxChatWindows: 3,
        colors: {
            primary: '#4C9A61',     // Verde naturaleza
            secondary: '#6B8E5A',   // Verde oliva
            light: '#D9E4D0',       // Verde muy pálido
            background: '#F7F4EB',  // Beige muy claro
            notification: '#E1953F' // Naranja/ámbar natural
        }
    };
    
    // Inicialización
    function init(options = {}) {
        // Configurar opciones
        config = Object.assign({}, config, options);
        
        debug(`Inicializando sistema de chat con opciones: ${JSON.stringify(config)}`);
        
        // Verificar que esté configurado correctamente
        if (!window.currentUserId) {
            debug('ERROR: currentUserId no está definido');
            console.error('Error: No se puede inicializar el chat sin un ID de usuario');
            return;
        }
        
        if (!window.chatApiUrls) {
            debug('ERROR: chatApiUrls no está definido');
            console.error('Error: No se pueden inicializar el chat sin las URLs de la API');
            return;
        }
        
        // Verificar APIs necesarias
        const requiredApis = ['getMessages', 'sendMessage', 'getConversations', 'getRoomInfo'];
        const missingApis = requiredApis.filter(api => !window.chatApiUrls[api]);
        
        if (missingApis.length > 0) {
            debug(`ERROR: Faltan las siguientes APIs: ${missingApis.join(', ')}`);
            console.error(`Error: Faltan las siguientes APIs: ${missingApis.join(', ')}`);
            return;
        }
        
        debug('Inicialización completada. Sistema de chat listo para usar.');
        debug(`Usuario actual: ${window.currentUserId}`);
        debug(`URLs API: ${JSON.stringify(window.chatApiUrls)}`);
        
        // Realizar verificación inicial de mensajes no leídos
        checkUnreadMessages();
        
        // Configurar verificación periódica
        setInterval(checkUnreadMessages, config.checkInterval || 30000);
        
        // Inicializar botón de chat flotante si existe
        const chatButton = document.getElementById('chat-main-button');
        if (chatButton) {
            initFloatingChatButton(chatButton);
        }
        
        // Inicializar los elementos que ya existen en el DOM
        document.querySelectorAll('[data-chat-room]').forEach(element => {
            initChatRoom(element);
        });
        
        // Crear intervalo para comprobar mensajes no leídos
        setInterval(checkUnreadMessages, config.updateInterval * 2);
        
        // Escuchar eventos para abrir chats
        document.addEventListener('openChat', function(e) {
            openChatWindow(e.detail.roomId, e.detail);
        });
    }
    
    // Inicializar botón flotante
    function initFloatingChatButton(button) {
        const conversationsPanel = document.getElementById('chat-conversations-panel');
        const notificationBadge = document.getElementById('chat-notification-count');
        
        // Mostrar/ocultar panel de conversaciones al hacer clic
        button.addEventListener('click', function() {
            if (conversationsPanel.style.display === 'none' || !conversationsPanel.style.display) {
                conversationsPanel.style.display = 'flex';
                loadConversations();
            } else {
                conversationsPanel.style.display = 'none';
            }
        });
        
        // Actualizar badge de notificaciones
        function updateNotificationBadge() {
            if (totalUnreadCount > 0) {
                notificationBadge.textContent = totalUnreadCount > 9 ? '9+' : totalUnreadCount;
                notificationBadge.style.display = 'flex';
            } else {
                notificationBadge.style.display = 'none';
            }
        }
        
        // Exponer función para actualizar el badge
        return {
            updateBadge: updateNotificationBadge
        };
    }
    
    // Inicializar un elemento de chat room
    function initChatRoom(element) {
        const roomId = element.getAttribute('data-chat-room');
        if (!roomId) return;
        
        // Registrar la ventana de chat
        chatWindows[roomId] = {
            element: element,
            lastMessageId: 0
        };
        
        // Configurar eventos para la ventana de chat
        setupChatWindowEvents(element, roomId);
        
        // Cargar mensajes iniciales
        loadMessages(roomId);
    }
    
    // Cargar lista de conversaciones
    function loadConversations() {
        const conversationsList = document.getElementById('chat-conversations-list');
        if (!conversationsList) return;
        
        // Mostrar indicador de carga
        conversationsList.innerHTML = '<div class="chat-loading"><i class="fas fa-spinner fa-spin"></i> Cargando...</div>';
        
        // Obtener conversaciones desde la API
        fetch(window.chatApiUrls.getConversations)
            .then(response => response.json())
            .then(data => {
                debug(`Datos de conversaciones recibidos: ${JSON.stringify(data)}`);
                
                if (data.status === 'success') {
                    renderConversations(conversationsList, data.conversations);
                    
                    // Actualizar contador global
                    totalUnreadCount = data.total_unread || 0;
                    updateAllNotifications();
                } else {
                    conversationsList.innerHTML = '<div class="p-3 text-center text-muted">Error al cargar las conversaciones</div>';
                }
            })
            .catch(error => {
                debug(`Error al cargar conversaciones: ${error}`);
                conversationsList.innerHTML = '<div class="p-3 text-center text-muted">Error al cargar las conversaciones</div>';
            });
    }
    
    // Renderizar lista de conversaciones
    function renderConversations(container, conversations) {
        if (!conversations || conversations.length === 0) {
            container.innerHTML = '<div class="p-3 text-center text-muted">No tienes conversaciones activas</div>';
            return;
        }
        
        let html = '';
        conversations.forEach(conversation => {
            // Crear avatar
            let avatarHtml = getAvatarHtml(conversation);
            
            // Determinar nombre a mostrar
            let displayName = getDisplayName(conversation);
            
            // Crear HTML de la conversación
            html += `
                <div class="chat-conversation-item" data-room-id="${conversation.id}">
                    <div class="chat-avatar">
                        ${avatarHtml}
                    </div>
                    <div class="chat-conversation- ">
                        <div class="chat-conversation-name">${displayName}</div>
                        <div class="chat-conversation-preview">
                            ${conversation.last_message ? 
                                (conversation.last_message.is_mine ? 'Tú: ' : 
                                    (conversation.last_message.sender_name ? conversation.last_message.sender_name + ': ' : '')) + 
                                    conversation.last_message.content 
                                : 'Sin mensajes'}
                        </div>
                    </div>
                    ${conversation.unread_count > 0 ? 
                        `<div class="chat-conversation-unread" title="${conversation.unread_count} mensajes sin leer">${conversation.unread_count}</div>` 
                        : ''}
                </div>
            `;
        });
        
        container.innerHTML = html;
        
        // Añadir eventos de clic para abrir conversaciones
        container.querySelectorAll('.chat-conversation-item').forEach(item => {
            item.addEventListener('click', function() {
                const roomId = this.getAttribute('data-room-id');
                debug(`Abriendo chat room ${roomId}`);
                
                // Cerrar panel de conversaciones
                const panel = document.getElementById('chat-conversations-panel');
                if (panel) panel.style.display = 'none';
                
                // Abrir ventana de chat
                openChatWindow(roomId);
            });
        });
    }
    
    // Función para obtener el avatar
    function getAvatarHtml(data) {
        if (data.avatar && data.avatar !== '') {
            return `<img src="${data.avatar}" alt="${data.name}" class="floating-chat-avatar">`;
        }
        
        let initials = '';
        if (data.username) {
            initials = data.username.substring(0, 2).toUpperCase();
        } else if (data.email) {
            initials = data.email.split('@')[0].substring(0, 2).toUpperCase();
        } else {
            initials = 'US';
        }
        
        return `<div class="floating-chat-avatar-initials">${initials}</div>`;
    }
    
    // Función para obtener el nombre de visualización
    function getDisplayName(userData) {
        if (userData.full_name && userData.full_name.trim() !== '') {
            return userData.full_name;
        } else if (userData.username && userData.username.trim() !== '') {
            return userData.username;
        } else if (userData.email) {
            return userData.email.split('@')[0];
        } else {
            return 'Usuario';
        }
    }
    
    // Abrir una ventana de chat
    function openChatWindow(roomId, options = {}) {
        // Si ya está abierta, enfocarla
        if (chatWindows[roomId]) {
            const existingWindow = chatWindows[roomId].element;
            // Implementación de "enfoque"
            existingWindow.classList.add('focus');
            setTimeout(() => {
                existingWindow.classList.remove('focus');
            }, 300);
            return chatWindows[roomId];
        }
        
        // Contenedor para ventanas flotantes
        const floatingContainer = document.getElementById('floating-chat-windows');
        if (!floatingContainer) return null;
        
        // Limitar número de ventanas activas
        const activeWindowIds = Object.keys(chatWindows);
        if (activeWindowIds.length >= config.maxChatWindows) {
            const oldestRoomId = activeWindowIds[0];
            closeChatWindow(oldestRoomId);
        }
        
        // Crear nueva ventana
        const chatWindow = document.createElement('div');
        chatWindow.className = 'floating-chat-window';
        chatWindow.id = `chat-window-${roomId}`;
        chatWindow.setAttribute('data-chat-room', roomId);
        
        // Estructura de la ventana
        chatWindow.innerHTML = `
            <div class="floating-chat-header">
                <div class="floating-chat-avatar"></div>
                <div class="floating-chat-title">Cargando...</div>
                <div class="floating-chat-actions">
                    <button class="floating-chat-action" data-action="minimize">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button class="floating-chat-action" data-action="close">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="floating-chat-messages">
                <div class="chat-loading">
                    <i class="fas fa-spinner fa-spin"></i> Cargando mensajes...
                </div>
            </div>
            <div class="floating-chat-input">
                <textarea placeholder="Escribe un mensaje..." rows="1"></textarea>
                <button type="button">
                    <i class="fas fa-paper-plane"></i>
                </button>
            </div>
        `;
        
        // Añadir al DOM
        floatingContainer.appendChild(chatWindow);
        
        // Registrar la ventana
        chatWindows[roomId] = {
            element: chatWindow,
            lastMessageId: 0
        };
        
        // Configurar eventos
        setupChatWindowEvents(chatWindow, roomId);
        
        // Cargar datos de la sala
        loadChatRoom(roomId);
        
        // Auto-resize para el textarea
        const textarea = chatWindow.querySelector('textarea');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 100) + 'px';
        });
        
        return chatWindows[roomId];
    }
    
    // Configurar eventos para ventana de chat
    function setupChatWindowEvents(chatWindow, roomId) {
        // Botón minimizar
        const minimizeBtn = chatWindow.querySelector('[data-action="minimize"]');
        if (minimizeBtn) {
            minimizeBtn.addEventListener('click', function() {
                chatWindow.classList.toggle('minimized');
                
                if (chatWindow.classList.contains('minimized')) {
                    chatWindow.style.height = '40px';
                    this.innerHTML = '<i class="fas fa-expand"></i>';
                } else {
                    chatWindow.style.height = '350px';
                    this.innerHTML = '<i class="fas fa-minus"></i>';
                }
            });
        }
        
        // Botón cerrar
        const closeBtn = chatWindow.querySelector('[data-action="close"]');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                closeChatWindow(roomId);
            });
        }
        
        // Enviar mensaje (botón)
        const sendBtn = chatWindow.querySelector('.floating-chat-input button');
        if (sendBtn) {
            sendBtn.addEventListener('click', function() {
                sendMessage(roomId);
            });
        }
        
        // Enviar mensaje con Enter
        const textarea = chatWindow.querySelector('textarea');
        if (textarea) {
            textarea.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage(roomId);
                }
            });
        }
        
        // Hacer la ventana arrastrable
        makeDraggable(chatWindow);
    }
    
    // Cerrar ventana de chat
    function closeChatWindow(roomId) {
        if (!chatWindows[roomId]) return;
        
        // Limpiar intervalo de actualización si existe
        if (chatUpdateIntervals[roomId]) {
            clearInterval(chatUpdateIntervals[roomId]);
            delete chatUpdateIntervals[roomId];
        }
        
        // Eliminar elemento DOM
        chatWindows[roomId].element.remove();
        
        // Eliminar referencia
        delete chatWindows[roomId];
    }
    
    // Cargar información de sala de chat
    function loadChatRoom(roomId) {
        if (!chatWindows[roomId]) return;
        
        const chatWindow = chatWindows[roomId].element;
        debug(`Cargando datos de sala ${roomId}`);
        
        fetch(`${window.chatApiUrls.getRoomInfo}?room_id=${roomId}`)
            .then(response => response.json())
            .then(data => {
                debug(`Datos de sala recibidos: ${JSON.stringify(data)}`);
                
                if (data.status === 'success') {
                    // Actualizar título
                    chatWindow.querySelector('.floating-chat-title').textContent = data.room.name;
                    
                    // Actualizar avatar
                    const avatarContainer = chatWindow.querySelector('.floating-chat-avatar');
                    if (data.room.profile_pic_url) {
                        avatarContainer.innerHTML = `<img src="${data.room.profile_pic_url}" alt="${data.room.name}">`;
                    } else {
                        const initialChar = data.room.is_group ? 
                            '<i class="fas fa-users"></i>' : 
                            `<span>${data.room.name.charAt(0)}</span>`;
                        avatarContainer.innerHTML = initialChar;
                    }
                    
                    // Almacenar info del room
                    chatWindows[roomId].info = data.room;
                    
                    // Cargar mensajes
                    loadMessages(roomId);
                } else {
                    showError(chatWindow, 'Error al cargar la conversación');
                }
            })
            .catch(error => {
                debug(`Error al cargar sala: ${error}`);
                showError(chatWindow, 'Error al cargar la conversación');
            });
    }
    
    // Cargar mensajes
    function loadMessages(roomId) {
        if (!chatWindows[roomId]) return;
        
        const chatWindow = chatWindows[roomId].element;
        const messagesContainer = chatWindow.querySelector('.floating-chat-messages');
        
        debug(`Cargando mensajes para sala ${roomId}`);
        
        // Mostrar indicador de carga
        messagesContainer.innerHTML = '<div class="chat-loading"><i class="fas fa-spinner fa-spin"></i> Cargando mensajes...</div>';
        
        // Verificar que la URL esté configurada correctamente
        const url = `${window.chatApiUrls.getMessages}${roomId}/`;
        debug(`Solicitando mensajes a URL: ${url}`);
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            }
        })
        .then(response => {
            debug(`Respuesta recibida: ${response.status}`);
            if (!response.ok) {
                debug(`Error HTTP: ${response.status} ${response.statusText}`);
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            debug(`Datos recibidos: ${JSON.stringify(data).substring(0, 250)}...`);
            
            if (data.status === 'success') {
                if (data.messages && Array.isArray(data.messages)) {
                    debug(`Número de mensajes recibidos: ${data.messages.length}`);
                    // Renderizar mensajes
                    renderMessages(messagesContainer, data.messages);
                    
                    // Actualizar último ID
                    if (data.messages.length > 0) {
                        chatWindows[roomId].lastMessageId = Math.max(...data.messages.map(m => m.id));
                        debug(`Último ID actualizado: ${chatWindows[roomId].lastMessageId}`);
                    }
                    
                    // Scroll al final
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    
                    // Activar actualizaciones periódicas
                    if (chatUpdateIntervals[roomId]) {
                        clearInterval(chatUpdateIntervals[roomId]);
                    }
                    
                    chatUpdateIntervals[roomId] = setInterval(() => {
                        updateMessages(roomId);
                    }, config.updateInterval || 5000);
                    
                    // Marcar mensajes como leídos
                    if (data.unread_messages && data.unread_messages.length > 0) {
                        markMessagesAsRead(data.unread_messages);
                    }
                } else {
                    debug('No hay mensajes o el formato es incorrecto');
                    messagesContainer.innerHTML = '<div class="p-3 text-center text-muted">No hay mensajes en esta conversación</div>';
                }
            } else {
                debug(`Error en respuesta: ${data.message || 'Sin mensaje de error'}`);
                messagesContainer.innerHTML = '<div class="p-3 text-center text-danger">Error al cargar los mensajes</div>';
            }
        })
        .catch(error => {
            debug(`Error al cargar mensajes: ${error.message}`);
            console.error('Error:', error);
            messagesContainer.innerHTML = '<div class="p-3 text-center text-danger">ERROR AL CARGAR LOS MENSAJES<br><small>Consulta la consola para más detalles</small></div>';
        });
    }
    
    // Renderizar mensajes
    function renderMessages(container, messages) {
        if (!messages || !Array.isArray(messages) || messages.length === 0) {
            container.innerHTML = '<div class="p-3 text-center text-muted">No hay mensajes en esta conversación</div>';
            return;
        }
        
        let html = '';
        try {
            messages.forEach(message => {
                html += createMessageHTML(message);
            });
            
            container.innerHTML = html;
            debug('Mensajes renderizados correctamente');
        } catch (error) {
            debug(`Error al renderizar mensajes: ${error.message}`);
            console.error('Error al renderizar mensajes:', error);
            container.innerHTML = '<div class="p-3 text-center text-danger">Error al mostrar los mensajes</div>';
        }
    }
    
    // Crear HTML para un mensaje
    function createMessageHTML(message) {
        const isMyMessage = message.is_mine || (message.sender && message.sender.id === window.currentUserId);
        
        // Obtener nombre para mostrar - PRIORIZAR USERNAME
        let senderName = 'Usuario';
        
        if (message.sender && message.sender.username) {
            senderName = message.sender.username;
        } else if (message.sender && message.sender.full_name) {
            senderName = message.sender.full_name;
        } else if (message.sender_name) {
            senderName = message.sender_name;
        } else if (message.sender && message.sender.email) {
            // Usar solo el nombre de usuario del email
            if (message.sender.email.includes('@')) {
                senderName = message.sender.email.split('@')[0];
            } else {
                senderName = message.sender.email;
            }
        }
        
        // Sanitizar el contenido HTML antes de mostrarlo
        const content = message.content
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
        
        // Formatear fecha (usar created_at para la compatibilidad)
        let timeStr = '';
        if (message.created_at) {
            try {
                const date = new Date(message.created_at);
                timeStr = `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
            } catch (e) {
                timeStr = message.created_at.toString();
            }
        }
        
        // Construir burbuja de chat con verificaciones adicionales
        return `
            <div class="message-bubble ${isMyMessage ? 'message-mine' : 'message-other'}" data-message-id="${message.id}">
                ${!isMyMessage && message.room_is_group ? `<div class="message-sender">${senderName}</div>` : ''}
                <div class="message-content">${content}</div>
                <div class="message-time">${timeStr}</div>
            </div>
        `;
    }
    
    // Actualizar mensajes (obtener solo los nuevos)
    function updateMessages(roomId) {
        if (!chatWindows[roomId]) return;
        
        const chatWindow = chatWindows[roomId].element;
        const messagesContainer = chatWindow.querySelector('.floating-chat-messages');
        const lastMessageId = chatWindows[roomId].lastMessageId || 0;
        
        // Solo actualizar si hay un ID válido
        if (!lastMessageId) {
            debug('No hay último ID para actualizar');
            return;
        }
        
        debug(`Actualizando mensajes para sala ${roomId}, último ID: ${lastMessageId}`);
        
        fetch(`${window.chatApiUrls.getMessages}${roomId}/?last_id=${lastMessageId}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Cache-Control': 'no-cache, no-store, must-revalidate'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            debug(`Respuesta de actualización: ${JSON.stringify(data).substring(0, 100)}...`);
            
            if (data.status === 'success' && data.messages && Array.isArray(data.messages) && data.messages.length > 0) {
                debug(`Nuevos mensajes recibidos: ${data.messages.length}`);
                
                // Comprobar si estamos en el fondo del scroll
                const isAtBottom = messagesContainer.scrollHeight - messagesContainer.scrollTop - messagesContainer.clientHeight < 50;
                
                // Añadir nuevos mensajes
                data.messages.forEach(message => {
                    // Solo añadir si no existe ya
                    if (!messagesContainer.querySelector(`[data-message-id="${message.id}"]`)) {
                        messagesContainer.insertAdjacentHTML('beforeend', createMessageHTML(message));
                        
                        // Disparar notificación si el mensaje no es del usuario actual
                        if (message.sender && message.sender.id !== window.currentUserId) {
                            // Comprobar si la página está visible
                            const isVisible = document.visibilityState === 'visible';
                            
                            // Disparar evento para notificación
                            document.dispatchEvent(new CustomEvent('newChatMessage', {
                                detail: {
                                    message: message,
                                    roomId: roomId,
                                    isVisible: isVisible
                                }
                            }));
                        }
                    }
                });
                
                // Actualizar último ID
                chatWindows[roomId].lastMessageId = Math.max(...data.messages.map(m => m.id), lastMessageId);
                debug(`Último ID actualizado a: ${chatWindows[roomId].lastMessageId}`);
                
                // Scroll al final si estaba al final antes
                if (isAtBottom) {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
                
                // Marcar mensajes como leídos
                if (data.unread_messages && data.unread_messages.length > 0) {
                    markMessagesAsRead(data.unread_messages);
                }
            }
        })
        .catch(error => {
            debug(`Error al actualizar mensajes: ${error.message}`);
        });
    }
    
    // Enviar mensaje
    function sendMessage(roomId) {
        if (!chatWindows[roomId]) return;
        
        const chatWindow = chatWindows[roomId].element;
        const textarea = chatWindow.querySelector('textarea');
        const content = textarea.value.trim();
        
        if (!content) return;
        
        debug(`Enviando mensaje a sala ${roomId}: ${content.substring(0, 30)}...`);
        
        textarea.disabled = true;
        
        fetch(`${window.chatApiUrls.sendMessage}${roomId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ content: content })
        })
        .then(response => response.json())
        .then(data => {
            textarea.disabled = false;
            
            if (data.status === 'success') {
                // Limpiar textarea
                textarea.value = '';
                textarea.style.height = 'auto';
                
                // Añadir el mensaje enviado a la conversación
                const messagesContainer = chatWindow.querySelector('.floating-chat-messages');
                messagesContainer.insertAdjacentHTML('beforeend', createMessageHTML(data.message));
                
                // Actualizar último ID
                chatWindows[roomId].lastMessageId = Math.max(chatWindows[roomId].lastMessageId || 0, data.message.id);
                
                // Scroll al final
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            } else {
                alert('Error al enviar el mensaje. Por favor, intenta de nuevo.');
            }
        })
        .catch(error => {
            textarea.disabled = false;
            debug(`Error al enviar mensaje: ${error}`);
            alert('Error al enviar el mensaje. Por favor, intenta de nuevo.');
        });
    }
    
    // Marcar mensajes como leídos
    function markMessagesAsRead(messageIds) {
        if (!messageIds || !Array.isArray(messageIds) || messageIds.length === 0) {
            return;
        }
        
        debug(`Marcando ${messageIds.length} mensajes como leídos`);
        
        // Usar Promise.all para manejar múltiples solicitudes en paralelo
        const markRequests = messageIds.map(messageId => {
            return fetch(window.chatApiUrls.markAsRead, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ message_id: messageId })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.status !== 'success') {
                    throw new Error(data.message || 'Error desconocido');
                }
                return true;
            })
            .catch(error => {
                debug(`Error al marcar mensaje ${messageId} como leído: ${error.message}`);
                return false;
            });
        });
        
        Promise.all(markRequests)
            .then(results => {
                const successCount = results.filter(Boolean).length;
                debug(`${successCount} de ${messageIds.length} mensajes marcados como leídos`);
                
                // Actualizar contadores tras marcar mensajes
                checkUnreadMessages();
            });
    }
    
    // Comprobar mensajes no leídos
    function checkUnreadMessages() {
        debug('Verificando mensajes no leídos');
        
        fetch(window.chatApiUrls.getConversations)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    let unreadCount = 0;
                    
                    if (data.conversations) {
                        unreadCount = data.conversations.reduce((total, conv) => {
                            return total + (conv.unread_count || 0);
                        }, 0);
                    } else if (data.total_unread !== undefined) {
                        unreadCount = data.total_unread;
                    }
                    
                    debug(`Total no leídos: ${unreadCount}`);
                    totalUnreadCount = unreadCount;
                    updateAllNotifications();
                }
            })
            .catch(error => {
                debug(`Error al verificar no leídos: ${error}`);
            });
    }
    
    // Actualizar todas las notificaciones
    function updateAllNotifications() {
        // Actualizar badge principal
        const notificationBadge = document.getElementById('chat-notification-count');
        if (notificationBadge) {
            if (totalUnreadCount > 0) {
                notificationBadge.textContent = totalUnreadCount > 9 ? '9+' : totalUnreadCount;
                notificationBadge.style.display = 'flex';
            } else {
                notificationBadge.style.display = 'none';
            }
        }
    }
    
    // Formatear una fecha
    function formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '';
        
        const now = new Date();
        const isToday = date.getDate() === now.getDate() && 
                      date.getMonth() === now.getMonth() && 
                      date.getFullYear() === now.getFullYear();
        
        if (isToday) {
            return date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
        } else {
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
        }
    }
    
    // Obtener el token CSRF de las cookies
    function getCsrfToken() {
        let cookieValue = null;
        
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Buscar la cookie con nombre csrftoken
                if (cookie.substring(0, 10) === 'csrftoken=') {
                    cookieValue = decodeURIComponent(cookie.substring(10));
                    break;
                }
            }
        }
        
        // Buscar en meta tags si no está en las cookies
        if (!cookieValue) {
            const metaTag = document.querySelector('meta[name="csrf-token"]');
            if (metaTag) {
                cookieValue = metaTag.getAttribute('content');
            }
        }
        
        // Si aún no se encuentra, buscar en inputs ocultos del formulario
        if (!cookieValue) {
            const inputTag = document.querySelector('input[name="csrfmiddlewaretoken"]');
            if (inputTag) {
                cookieValue = inputTag.value;
            }
        }
        
        if (!cookieValue) {
            debug('ADVERTENCIA: No se pudo encontrar el token CSRF');
        }
        
        return cookieValue;
    }
    
    // Hacer un elemento arrastrable
    function makeDraggable(element) {
        const header = element.querySelector('.floating-chat-header');
        if (!header) return;
        
        let isDragging = false;
        let offsetX, offsetY;
        
        header.addEventListener('mousedown', function(e) {
            // No arrastrar si se hace clic en botones
            if (e.target.closest('.floating-chat-action')) return;
            
            isDragging = true;
            offsetX = e.clientX - element.getBoundingClientRect().left;
            offsetY = e.clientY - element.getBoundingClientRect().top;
            
            // Evitar selección de texto
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', function(e) {
            if (!isDragging) return;
            
            const x = e.clientX - offsetX;
            const y = e.clientY - offsetY;
            
            // Limitar al viewport
            const maxX = window.innerWidth - element.offsetWidth;
            const maxY = window.innerHeight - element.offsetHeight;
            
            element.style.position = 'fixed';
            element.style.left = Math.min(Math.max(0, x), maxX) + 'px';
            element.style.top = Math.min(Math.max(0, y), maxY) + 'px';
        });
        
        document.addEventListener('mouseup', function() {
            isDragging = false;
        });
    }
    
    // Mostrar error genérico
    function showError(container, message) {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        
        if (!container) return;
        
        if (container.classList.contains('floating-chat-messages')) {
            container.innerHTML = `<div class="p-3 text-center text-danger">${message}</div>`;
        } else {
            const messagesContainer = container.querySelector('.floating-chat-messages');
            if (messagesContainer) {
                messagesContainer.innerHTML = `<div class="p-3 text-center text-danger">${message}</div>`;
            }
        }
    }
    
    // Debug función para agregar logs
    function debug(message) {
        console.log(`[Chat Debug]: ${message}`);
    }
    
    // Exponer API pública
    return {
        init: init,
        openChat: openChatWindow,
        closeChat: closeChatWindow,
        updateChat: updateMessages,
        checkUnread: checkUnreadMessages,
        config: config
    };
})();

// Función de debug global para uso fuera del módulo
function debug(message) {
    console.log(`[Chat Debug]: ${message}`);
}

// Inicializar automáticamente cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Comprobar que exista la configuración necesaria
    if (window.currentUserId && window.chatApiUrls) {
        debug('Configuración de chat detectada. Inicializando...');
        debug(`Usuario actual: ${window.currentUserId}`);
        debug(`URL API: ${JSON.stringify(window.chatApiUrls)}`);
        
        // Inicializar el sistema de chat
        try {
            window.CampoUnidoChat.init();
            debug('Chat inicializado correctamente');
        } catch (e) {
            console.error('[Chat Error]:', e);
        }
    } else {
        console.error('[Chat Error]: No se pudo inicializar el chat. Faltan currentUserId o chatApiUrls.');
        if (!window.currentUserId) console.error('currentUserId no está definido');
        if (!window.chatApiUrls) console.error('chatApiUrls no está definido');
    }
});

// Formatear el nombre de la sala
function formatChatName(data) {
    if (!data) return 'Chat';
    
    if (data.is_group) {
        return data.name || 'Grupo';
    }
    
    if (data.other_user) {
        // Priorizar username sobre otros campos
        if (data.other_user.username) {
            return data.other_user.username;
        } else if (data.other_user.email) {
            // Usar parte del email antes del @
            const emailParts = data.other_user.email.split('@');
            return emailParts[0] || data.other_user.email;
        }
    }
    
    return data.name || 'Chat';
}

// Crear HTML para avatar (para compatibilidad)
function createAvatarHtml(data) {
    return getAvatarHtml(data);
}

// Renderizar un mensaje
function renderMessage(message, isCurrentUser, previousSender) {
    let messageClass = isCurrentUser ? 'sent' : 'received';
    let bubbleClass = isCurrentUser ? 'sent-bubble' : 'received-bubble';
    let showSender = !isCurrentUser && previousSender !== message.sender.id;
    
    // Usar getDisplayName para mostrar el nombre del remitente
    let senderName = message.sender ? getDisplayName(message.sender) : 'Usuario';
    
    let messageTime = formatMessageTime(message.timestamp);
    
    let html = `
        <div class="floating-chat-message ${messageClass}">
            ${showSender ? `<div class="floating-chat-sender">${senderName}</div>` : ''}
            <div class="floating-chat-bubble ${bubbleClass}">
                ${message.content}
                <span class="floating-chat-time">${messageTime}</span>
            </div>
        </div>
    `;
    
    return html;
}

// Manejar un mensaje recibido
function handleReceivedMessage(message, roomId) {
    let chatWindow = document.querySelector(`.floating-chat-window[data-room-id="${roomId}"]`);
    if (!chatWindow) return;
    
    let messagesContainer = chatWindow.querySelector('.floating-chat-messages');
    let currentUserId = document.body.getAttribute('data-user-id');
    let isCurrentUser = message.sender.id == currentUserId;
    
    // Determinar el remitente anterior
    let lastMessage = chatWindow.querySelector('.floating-chat-message:last-child');
    let previousSender = lastMessage ? lastMessage.getAttribute('data-sender-id') : null;
    
    // Usar getDisplayName para el nombre del remitente
    let senderName = message.sender ? getDisplayName(message.sender) : 'Usuario';
    
    let messageTime = formatMessageTime(message.timestamp);
    
    let html = `
        <div class="floating-chat-message ${isCurrentUser ? 'sent' : 'received'}" data-sender-id="${message.sender.id}">
            ${!isCurrentUser && previousSender !== message.sender.id ? 
              `<div class="floating-chat-sender">${senderName}</div>` : ''}
            <div class="floating-chat-bubble ${isCurrentUser ? 'sent-bubble' : 'received-bubble'}">
                ${message.content}
                <span class="floating-chat-time">${messageTime}</span>
            </div>
        </div>
    `;
    
    messagesContainer.insertAdjacentHTML('beforeend', html);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    // Actualizar el contador de mensajes
    updateUnreadCount(roomId, false);
} 