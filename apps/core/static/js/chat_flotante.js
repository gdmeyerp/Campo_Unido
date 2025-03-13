
document.addEventListener('DOMContentLoaded', function() {
    // Variables principales
    const chatMainButton = document.getElementById('chat-main-button');
    const chatConversationsPanel = document.getElementById('chat-conversations-panel');
    const chatConversationsList = document.getElementById('chat-conversations-list');
    const floatingChatWindows = document.getElementById('floating-chat-windows');
    const notificationBadge = document.getElementById('chat-notification-count');
    
    let activeConversations = [];
    let totalUnread = 0;
    let chatUpdateIntervals = {}; // Para almacenar los intervalos por sala
    
    // Función para actualizar la notificación
    function updateNotificationBadge() {
        if (totalUnread > 0) {
            notificationBadge.innerText = totalUnread > 9 ? '9+' : totalUnread;
            notificationBadge.style.display = 'flex';
        } else {
            notificationBadge.style.display = 'none';
        }
    }
    
    // Alternar panel de conversaciones
    chatMainButton.addEventListener('click', function() {
        if (chatConversationsPanel.style.display === 'none' || chatConversationsPanel.style.display === '') {
            chatConversationsPanel.style.display = 'flex';
            loadConversations();
        } else {
            chatConversationsPanel.style.display = 'none';
        }
    });
    
    // Debug función para agregar logs
    function debug(message) {
        console.log(`[Chat Debug]: ${message}`);
    }
    
    // Cargar conversaciones
    function loadConversations() {
        // Mostrar indicador de carga
        chatConversationsList.innerHTML = '<div class="chat-loading"><i class="fas fa-spinner fa-spin"></i> Cargando...</div>';
        debug('Cargando conversaciones...');
        
        // Realizar petición AJAX para obtener las conversaciones
        fetch('{% url "chat:get_conversations" %}')
            .then(response => {
                debug(`Respuesta recibida: ${response.status}`);
                return response.json();
            })
            .then(data => {
                debug(`Datos recibidos: ${JSON.stringify(data)}`);
                if (data.status === 'success') {
                    renderConversations(data.conversations);
                    totalUnread = data.total_unread;
                    updateNotificationBadge();
                } else {
                    chatConversationsList.innerHTML = '<div class="p-3 text-center text-muted">Error al cargar las conversaciones</div>';
                }
            })
            .catch(error => {
                debug(`Error al cargar conversaciones: ${error}`);
                console.error('Error:', error);
                chatConversationsList.innerHTML = '<div class="p-3 text-center text-muted">Error al cargar las conversaciones</div>';
            });
    }
    
    // Renderizar conversaciones
    function renderConversations(conversations) {
        if (conversations.length === 0) {
            chatConversationsList.innerHTML = '<div class="p-3 text-center text-muted">No tienes conversaciones activas</div>';
            return;
        }
        
        let html = '';
        conversations.forEach(conversation => {
            // Manejar la imagen de perfil
            let avatarHtml = '';
            
            if (conversation.is_group) {
                avatarHtml = `<div class="chat-avatar-text"><i class="fas fa-users"></i></div>`;
            } else if (conversation.other_user && conversation.other_user.profile_picture) {
                avatarHtml = `<img src="${conversation.other_user.profile_picture}" class="chat-avatar-img" alt="${conversation.other_user.username}">`;
            } else {
                let initial = '';
                if (conversation.is_group) {
                    initial = '<i class="fas fa-users"></i>';
                } else if (conversation.other_user && conversation.other_user.username) {
                    initial = conversation.other_user.username.charAt(0);
                } else if (conversation.name) {
                    initial = conversation.name.charAt(0);
                } else {
                    initial = '<i class="fas fa-user"></i>';
                }
                avatarHtml = `<div class="chat-avatar-text">${initial}</div>`;
            }
            
            // Determinar el nombre a mostrar
            let displayName = '';
            if (conversation.is_group) {
                displayName = conversation.name;
            } else if (conversation.other_user) {
                displayName = conversation.other_user.full_name || conversation.other_user.username;
            } else {
                displayName = conversation.name;
            }
            
            html += `
                <div class="chat-conversation-item" data-room-id="${conversation.id}">
                    <div class="chat-avatar">
                        ${avatarHtml}
                    </div>
                    <div class="chat-conversation-details">
                        <div class="chat-conversation-name">${displayName}</div>
                        <div class="chat-conversation-preview">
                            ${conversation.last_message ? 
                                (conversation.last_message.is_mine ? 'Tú: ' : (conversation.last_message.sender_name ? conversation.last_message.sender_name + ': ' : '')) + conversation.last_message.content 
                                : 'Sin mensajes'}
                        </div>
                    </div>
                    ${conversation.unread_count > 0 ? 
                        `<div class="chat-conversation-unread" title="${conversation.unread_count} mensajes sin leer">${conversation.unread_count}</div>` 
                        : ''}
                </div>
            `;
        });
        
        chatConversationsList.innerHTML = html;
        
        // Agregar eventos a las conversaciones
        document.querySelectorAll('.chat-conversation-item').forEach(item => {
            item.addEventListener('click', function() {
                const roomId = this.getAttribute('data-room-id');
                debug(`Abriendo chat room ${roomId}`);
                openChatWindow(roomId);
                chatConversationsPanel.style.display = 'none';
            });
        });
    }
    
    // Abrir ventana de chat
    function openChatWindow(roomId) {
        // Verificar si la ventana ya está abierta
        if (activeConversations.includes(roomId)) {
            // Enfocar la ventana existente
            document.getElementById(`chat-window-${roomId}`).classList.add('focus');
            setTimeout(() => {
                document.getElementById(`chat-window-${roomId}`).classList.remove('focus');
            }, 300);
            return;
        }
        
        // Limitar a 3 ventanas activas
        if (activeConversations.length >= 3) {
            const oldestRoomId = activeConversations.shift();
            const oldWindow = document.getElementById(`chat-window-${oldestRoomId}`);
            if (oldWindow) {
                // Limpiar el intervalo si existe
                if (chatUpdateIntervals[oldestRoomId]) {
                    clearInterval(chatUpdateIntervals[oldestRoomId]);
                    delete chatUpdateIntervals[oldestRoomId];
                }
                oldWindow.remove();
            }
        }
        
        // Crear nueva ventana
        const chatWindow = document.createElement('div');
        chatWindow.className = 'floating-chat-window';
        chatWindow.id = `chat-window-${roomId}`;
        
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
        
        floatingChatWindows.appendChild(chatWindow);
        activeConversations.push(roomId);
        
        // Cargar datos de la conversación
        loadChatRoom(roomId);
        
        // Agregar eventos a la ventana
        setupChatWindowEvents(chatWindow, roomId);
        
        // Auto-resize textarea
        const textarea = chatWindow.querySelector('textarea');
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight < 100 ? this.scrollHeight : 100) + 'px';
        });
    }
    
    // Configurar eventos de la ventana de chat
    function setupChatWindowEvents(chatWindow, roomId) {
        // Minimizar
        chatWindow.querySelector('[data-action="minimize"]').addEventListener('click', function() {
            chatWindow.classList.toggle('minimized');
            if (chatWindow.classList.contains('minimized')) {
                chatWindow.style.height = '40px';
                this.innerHTML = '<i class="fas fa-expand"></i>';
            } else {
                chatWindow.style.height = '350px';
                this.innerHTML = '<i class="fas fa-minus"></i>';
            }
        });
        
        // Cerrar
        chatWindow.querySelector('[data-action="close"]').addEventListener('click', function() {
            // Limpiar el intervalo si existe
            if (chatUpdateIntervals[roomId]) {
                clearInterval(chatUpdateIntervals[roomId]);
                delete chatUpdateIntervals[roomId];
            }
            chatWindow.remove();
            activeConversations = activeConversations.filter(id => id !== roomId);
        });
        
        // Enviar mensaje
        const sendForm = chatWindow.querySelector('.floating-chat-input');
        sendForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage(roomId, chatWindow);
        });
        
        sendForm.querySelector('button').addEventListener('click', function() {
            sendMessage(roomId, chatWindow);
        });
        
        // Enter para enviar
        const textarea = chatWindow.querySelector('textarea');
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage(roomId, chatWindow);
            }
        });
        
        // Hacer ventana arrastrable
        makeDraggable(chatWindow);
    }
    
    // Cargar datos de la sala de chat
    function loadChatRoom(roomId) {
        const chatWindow = document.getElementById(`chat-window-${roomId}`);
        if (!chatWindow) return;
        
        debug(`Cargando datos de sala ${roomId}`);
        
        fetch(`${window.chatApiUrls.getRoomInfo}?room_id=${roomId}`)
            .then(response => {
                debug(`Respuesta de get_room_info: ${response.status}`);
                return response.json();
            })
            .then(data => {
                debug(`Datos de sala recibidos: ${JSON.stringify(data)}`);
                if (data.status === 'success') {
                    // Actualizar título
                    chatWindow.querySelector('.floating-chat-title').innerText = data.room.name;
                    
                    // Actualizar avatar
                    const avatarContainer = chatWindow.querySelector('.floating-chat-avatar');
                    if (data.room.profile_pic_url) {
                        avatarContainer.innerHTML = `<img src="${data.room.profile_pic_url}" alt="${data.room.name}">`;
                    } else {
                        avatarContainer.innerHTML = data.room.is_group ? 
                            '<i class="fas fa-users"></i>' : 
                            `<span>${data.room.name.charAt(0)}</span>`;
                    }
                    
                    // Cargar mensajes
                    loadMessages(roomId);
                } else {
                    showError(chatWindow, 'Error al cargar la conversación');
                }
            })
            .catch(error => {
                debug(`Error al cargar sala: ${error}`);
                console.error('Error:', error);
                showError(chatWindow, 'Error al cargar la conversación');
            });
    }
    
    // Cargar mensajes
    function loadMessages(roomId) {
        const chatWindow = document.getElementById(`chat-window-${roomId}`);
        if (!chatWindow) return;
        
        const messagesContainer = chatWindow.querySelector('.floating-chat-messages');
        
        debug(`Cargando mensajes para sala ${roomId}`);
        
        fetch(`${window.chatApiUrls.getMessages}${roomId}/`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => {
                debug(`Respuesta de get_messages: ${response.status}`);
                return response.json();
            })
            .then(data => {
                debug(`Datos de mensajes recibidos: ${JSON.stringify(data).substring(0, 200)}...`);
                if (data.status === 'success') {
                    renderMessages(messagesContainer, data.messages);
                    
                    // Scroll al final
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    
                    // Activar actualizaciones periódicas
                    if (chatUpdateIntervals[roomId]) {
                        clearInterval(chatUpdateIntervals[roomId]);
                    }
                    
                    chatUpdateIntervals[roomId] = setInterval(() => {
                        updateMessages(roomId);
                    }, 5000);
                } else {
                    showError(messagesContainer, 'Error al cargar los mensajes');
                }
            })
            .catch(error => {
                debug(`Error al cargar mensajes: ${error}`);
                console.error('Error:', error);
                showError(messagesContainer, 'Error al cargar los mensajes');
            });
    }
    
    // Renderizar mensajes
    function renderMessages(container, messages) {
        if (!messages || messages.length === 0) {
            container.innerHTML = '<div class="p-3 text-center text-muted">No hay mensajes en esta conversación</div>';
            return;
        }
        
        let html = '';
        messages.forEach(message => {
            html += createMessageHTML(message);
        });
        
        container.innerHTML = html;
    }
    
    // Crear HTML de mensaje
    function createMessageHTML(message) {
        // Avatar para mensajes
        let avatarHtml = '';
        if (!message.is_mine) {
            if (message.profile_pic_url) {
                avatarHtml = `<img src="${message.profile_pic_url}" class="message-avatar" alt="${message.sender}">`;
            } else {
                avatarHtml = `<div class="message-avatar-text">${message.sender.charAt(0)}</div>`;
            }
        }
        
        return `
            <div class="floating-chat-message ${message.is_mine ? 'own' : ''}" data-message-id="${message.id}">
                ${!message.is_mine ? avatarHtml : ''}
                <div class="floating-chat-message-bubble">
                    ${message.content.replace(/\n/g, '<br>')}
                    <div class="floating-chat-time">${message.timestamp}</div>
                </div>
            </div>
        `;
    }
    
    // Actualizar mensajes
    function updateMessages(roomId) {
        const chatWindow = document.getElementById(`chat-window-${roomId}`);
        if (!chatWindow) return;
        
        const messagesContainer = chatWindow.querySelector('.floating-chat-messages');
        const messages = messagesContainer.querySelectorAll('.floating-chat-message');
        let lastId = 0;
        
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            lastId = lastMessage.getAttribute('data-message-id');
        }
        
        debug(`Actualizando mensajes para sala ${roomId}, último ID: ${lastId}`);
        
        fetch(`${window.chatApiUrls.getMessages}${roomId}/?last_id=${lastId}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.messages && data.messages.length > 0) {
                    debug(`Nuevos mensajes recibidos: ${data.messages.length}`);
                    // Añadir nuevos mensajes
                    data.messages.forEach(message => {
                        messagesContainer.insertAdjacentHTML('beforeend', createMessageHTML(message));
                    });
                    
                    // Scroll al final
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    
                    // Actualizar contador de no leídos
                    checkUnreadMessages();
                }
            })
            .catch(error => {
                debug(`Error al actualizar mensajes: ${error}`);
                console.error('Error:', error);
            });
    }
    
    // Enviar mensaje
    function sendMessage(roomId, chatWindow) {
        const textarea = chatWindow.querySelector('textarea');
        const content = textarea.value.trim();
        
        if (!content) return;
        
        debug(`Enviando mensaje a sala ${roomId}: ${content.substring(0, 30)}...`);
        
        textarea.disabled = true;
        
        fetch(`${window.chatApiUrls.sendMessage}${roomId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest'
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
                
                // Actualizar mensajes
                updateMessages(roomId);
            } else {
                debug(`Error al enviar mensaje: ${JSON.stringify(data)}`);
                alert('Error al enviar el mensaje. Por favor, intenta de nuevo.');
            }
        })
        .catch(error => {
            textarea.disabled = false;
            debug(`Error al enviar mensaje: ${error}`);
            console.error('Error:', error);
            alert('Error al enviar el mensaje. Por favor, intenta de nuevo.');
        });
    }
    
    // Mostrar error
    function showError(container, message) {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        
        if (container) {
            if (container.classList.contains('floating-chat-messages')) {
                container.innerHTML = `<div class="p-3 text-center text-danger">${message}</div>`;
            } else {
                const messagesContainer = container.querySelector('.floating-chat-messages');
                if (messagesContainer) {
                    messagesContainer.innerHTML = `<div class="p-3 text-center text-danger">${message}</div>`;
                }
            }
        }
    }
    
    // Hacer elemento arrastrable
    function makeDraggable(element) {
        const header = element.querySelector('.floating-chat-header');
        let isDragging = false;
        let offsetX, offsetY;
        
        header.addEventListener('mousedown', function(e) {
            if (e.target.closest('.floating-chat-action')) return; // No arrastrar si se hace clic en botones
            
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
    
    // Verificar mensajes no leídos
    function checkUnreadMessages() {
        debug('Verificando mensajes no leídos');
        
        fetch('{% url "chat:get_conversations" %}')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    let unreadCount = 0;
                    if (data.conversations) {
                        data.conversations.forEach(conversation => {
                            if (conversation.unread_count) {
                                unreadCount += conversation.unread_count;
                            }
                        });
                    }
                    debug(`Total no leídos: ${unreadCount}`);
                    totalUnread = unreadCount;
                    updateNotificationBadge();
                }
            })
            .catch(error => {
                debug(`Error al verificar no leídos: ${error}`);
                console.error('Error:', error);
            });
    }
    
    // Cargar inicialmente los mensajes no leídos
    checkUnreadMessages();
});