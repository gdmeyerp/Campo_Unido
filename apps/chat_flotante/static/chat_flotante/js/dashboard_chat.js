/**
 * Dashboard Chat - Módulo de chat para el dashboard estilo Facebook
 */
document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const dashboardChatSearch = document.getElementById('dashboard-chat-search');
    const dashboardChatSearchBox = document.getElementById('dashboard-chat-search-box');
    const dashboardChatSearchInput = document.getElementById('dashboard-chat-search-input');
    const dashboardChatSearchClose = document.getElementById('dashboard-chat-search-close');
    const dashboardNewChat = document.getElementById('dashboard-new-chat');
    const dashboardNewChatModal = document.getElementById('dashboard-new-chat-modal');
    const dashboardConversationsList = document.getElementById('dashboard-conversations-list');
    const dashboardChatEmpty = document.getElementById('dashboard-chat-empty');
    const dashboardChatConversation = document.getElementById('dashboard-chat-conversation');
    const dashboardChatMessages = document.getElementById('dashboard-chat-messages');
    const dashboardChatMessageInput = document.getElementById('dashboard-chat-message-input');
    const dashboardChatSendButton = document.getElementById('dashboard-chat-send-button');
    const dashboardChatUserSearch = document.getElementById('dashboard-chat-user-search');
    const dashboardChatUserResults = document.getElementById('dashboard-chat-user-results');
    const messageForm = document.getElementById('message-form');
    const imageInput = document.getElementById('dashboard-chat-image-input');
    const imagePreviewContainer = document.getElementById('image-preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeImageBtn = document.getElementById('remove-image-btn');
    const emojiButton = document.getElementById('dashboard-chat-emoji-button');
    const emojiPickerContainer = document.getElementById('emoji-picker-container');
    
    // Estado de la aplicación
    let activeRoomId = null;
    let conversations = [];
    let messagesUpdateInterval = null;
    let searchTimeout = null;
    let selectedImage = null;
    
    // Emojis comunes agrupados por categoría
    const emojiGroups = {
        'Rostros sonrientes': ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌'],
        'Amor y corazones': ['😍', '🥰', '😘', '😗', '😙', '😚', '❤️', '💛', '💚', '💙', '💜', '🧡', '🖤', '💕'],
        'Manos y gestos': ['👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '👊', '👏', '🙌', '🤝', '💪', '🙏', '👋'],
        'Animales': ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🦁', '🐮', '🐷', '🐸', '🐵'],
        'Comida': ['🍏', '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🍈', '🍒', '🍑', '🥭', '🍍'],
        'Actividad': ['⚽️', '🏀', '🏈', '⚾️', '🥎', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🏒', '🏑', '🥅']
    };
    
    // Inicializar el chat
    initDashboardChat();
    
    /**
     * Inicializa el chat del dashboard
     */
    function initDashboardChat() {
        // Cargar conversaciones al iniciar
        loadConversations();
        
        // Configurar eventos
        setupEventListeners();
        
        // Auto-resize del área de texto
        setupTextareaAutoResize();
        
        // Inicializar emoji picker
        initEmojiPicker();
    }
    
    /**
     * Configura todos los event listeners
     */
    function setupEventListeners() {
        // Botón de búsqueda
        if (dashboardChatSearch) {
            dashboardChatSearch.addEventListener('click', function() {
                dashboardChatSearchBox.style.display = 'block';
                dashboardChatSearchInput.focus();
            });
        }
        
        // Botón de cerrar búsqueda
        if (dashboardChatSearchClose) {
            dashboardChatSearchClose.addEventListener('click', function() {
                dashboardChatSearchBox.style.display = 'none';
                dashboardChatSearchInput.value = '';
                loadConversations(); // Recargar conversaciones originales
            });
        }
        
        // Input de búsqueda
        if (dashboardChatSearchInput) {
            dashboardChatSearchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                const query = this.value.trim();
                
                searchTimeout = setTimeout(() => {
                    if (query.length > 0) {
                        searchConversations(query);
                    } else {
                        loadConversations();
                    }
                }, 300);
            });
        }
        
        // Botón de nueva conversación
        if (dashboardNewChat) {
            dashboardNewChat.addEventListener('click', function() {
                $(dashboardNewChatModal).modal('show');
                if (dashboardChatUserSearch) {
                    dashboardChatUserSearch.value = '';
                }
                if (dashboardChatUserResults) {
                    // Mostrar mensaje de carga
                    dashboardChatUserResults.innerHTML = `
                        <div class="chat-loading">
                            <i class="fas fa-spinner fa-spin"></i> Cargando usuarios...
                        </div>
                    `;
                    
                    // Cargar usuarios sugeridos automáticamente
                    loadSuggestedUsers();
                }
            });
        }
        
        // Input de búsqueda de usuarios
        if (dashboardChatUserSearch) {
            dashboardChatUserSearch.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                const query = this.value.trim();
                
                searchTimeout = setTimeout(() => {
                    if (query.length > 1) {
                        searchUsers(query);
                    } else {
                        dashboardChatUserResults.innerHTML = '';
                    }
                }, 300);
            });
        }
        
        // Enviar mensaje con el botón
        if (dashboardChatSendButton) {
            dashboardChatSendButton.addEventListener('click', sendMessage);
        }
        
        // Enviar mensaje con Enter
        if (dashboardChatMessageInput) {
            dashboardChatMessageInput.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
        }
        
        // Input de imagen
        if (imageInput) {
            imageInput.addEventListener('change', function() {
                handleImageSelection(this);
            });
        }
        
        // Botón de eliminar imagen
        if (removeImageBtn) {
            removeImageBtn.addEventListener('click', function() {
                clearSelectedImage();
            });
        }
        
        // Botón de emoji
        if (emojiButton) {
            emojiButton.addEventListener('click', function() {
                toggleEmojiPicker();
            });
        }
        
        // Cerrar el selector de emojis al hacer clic fuera
        document.addEventListener('click', function(event) {
            if (emojiPickerContainer && emojiPickerContainer.style.display === 'block') {
                if (!emojiPickerContainer.contains(event.target) && event.target !== emojiButton) {
                    emojiPickerContainer.style.display = 'none';
                }
            }
        });
        
        // Evento para mostrar imagen en pantalla completa
        document.addEventListener('click', function(event) {
            if (event.target.classList.contains('message-image')) {
                showFullscreenImage(event.target.src);
            }
            
            if (event.target.classList.contains('fullscreen-image-overlay')) {
                document.querySelector('.fullscreen-image-overlay').remove();
            }
        });
    }
    
    /**
     * Maneja la selección de imágenes
     */
    function handleImageSelection(input) {
        if (input.files && input.files[0]) {
            const file = input.files[0];
            
            // Verificar tipo de archivo
            if (!file.type.match('image.*')) {
                alert('Por favor, selecciona una imagen válida.');
                input.value = '';
                return;
            }
            
            // Verificar tamaño (máximo 5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('La imagen no debe superar los 5MB.');
                input.value = '';
                return;
            }
            
            // Guardar referencia a la imagen
            selectedImage = file;
            
            // Mostrar vista previa
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreviewContainer.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    }
    
    /**
     * Limpia la imagen seleccionada
     */
    function clearSelectedImage() {
        selectedImage = null;
        imageInput.value = '';
        imagePreviewContainer.style.display = 'none';
    }
    
    /**
     * Inicializa el selector de emojis
     */
    function initEmojiPicker() {
        if (!emojiPickerContainer) return;
        
        let html = '';
        
        // Generar HTML para cada grupo de emojis
        for (const [groupName, emojis] of Object.entries(emojiGroups)) {
            html += `
                <div class="emoji-group">
                    <div class="emoji-group-title">${groupName}</div>
                    <div class="emoji-grid">
            `;
            
            emojis.forEach(emoji => {
                html += `<div class="emoji-item" data-emoji="${emoji}">${emoji}</div>`;
            });
            
            html += `
                    </div>
                </div>
            `;
        }
        
        emojiPickerContainer.innerHTML = html;
        
        // Agregar event listeners a los emojis
        document.querySelectorAll('.emoji-item').forEach(item => {
            item.addEventListener('click', function() {
                insertEmoji(this.getAttribute('data-emoji'));
            });
        });
    }
    
    /**
     * Muestra u oculta el selector de emojis
     */
    function toggleEmojiPicker() {
        if (emojiPickerContainer.style.display === 'block') {
            emojiPickerContainer.style.display = 'none';
        } else {
            emojiPickerContainer.style.display = 'block';
        }
    }
    
    /**
     * Inserta un emoji en el textarea
     */
    function insertEmoji(emoji) {
        if (!dashboardChatMessageInput) return;
        
        // Obtener posición del cursor
        const start = dashboardChatMessageInput.selectionStart;
        const end = dashboardChatMessageInput.selectionEnd;
        const text = dashboardChatMessageInput.value;
        
        // Insertar emoji en la posición actual
        dashboardChatMessageInput.value = text.substring(0, start) + emoji + text.substring(end);
        
        // Mover el cursor después del emoji
        dashboardChatMessageInput.selectionStart = dashboardChatMessageInput.selectionEnd = start + emoji.length;
        
        // Enfocar el textarea
        dashboardChatMessageInput.focus();
    }
    
    /**
     * Muestra una imagen en pantalla completa
     */
    function showFullscreenImage(src) {
        // Crear overlay
        const overlay = document.createElement('div');
        overlay.className = 'fullscreen-image-overlay';
        
        // Crear imagen
        const img = document.createElement('img');
        img.src = src;
        img.className = 'fullscreen-image';
        
        // Agregar al DOM
        overlay.appendChild(img);
        document.body.appendChild(overlay);
    }
    
    /**
     * Configura el auto-resize del textarea
     */
    function setupTextareaAutoResize() {
        if (dashboardChatMessageInput) {
            dashboardChatMessageInput.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight < 120 ? this.scrollHeight : 120) + 'px';
            });
        }
    }
    
    /**
     * Carga las conversaciones del usuario
     */
    function loadConversations() {
        if (!dashboardConversationsList) return;
        
        dashboardConversationsList.innerHTML = `
            <div class="chat-loading">
                <i class="fas fa-spinner fa-spin"></i> Cargando conversaciones...
            </div>
        `;
        
        // Obtener conversaciones vía AJAX
        fetch('/chat/api/conversaciones/')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    conversations = data.conversations;
                    renderConversations(conversations);
                    
                    // Si hay una conversación activa, actualizar unread count
                    if (activeRoomId) {
                        updateActiveConversation();
                    }
                } else {
                    dashboardConversationsList.innerHTML = `
                        <div class="p-3 text-center text-muted">
                            Error al cargar las conversaciones
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error al cargar conversaciones:', error);
                dashboardConversationsList.innerHTML = `
                    <div class="p-3 text-center text-muted">
                        Error al cargar las conversaciones
                    </div>
                `;
            });
    }
    
    /**
     * Renderiza la lista de conversaciones
     */
    function renderConversations(conversations) {
        if (!dashboardConversationsList) return;
        
        if (!conversations || conversations.length === 0) {
            dashboardConversationsList.innerHTML = `
                <div class="p-3 text-center text-muted">
                    No tienes conversaciones activas
                </div>
            `;
            return;
        }
        
        let html = '';
        
        conversations.forEach(conversation => {
            // Preparar avatar
            let avatarHtml = '';
            
            if (conversation.is_group) {
                avatarHtml = `<div class="dashboard-conversation-avatar-text"><i class="fas fa-users"></i></div>`;
            } else if (conversation.other_user && conversation.other_user.profile_picture) {
                avatarHtml = `<img src="${conversation.other_user.profile_picture}" alt="${conversation.other_user.display_name}">`;
            } else {
                const initial = conversation.is_group ? 
                    '<i class="fas fa-users"></i>' : 
                    ((conversation.other_user && conversation.other_user.display_name) ? 
                        conversation.other_user.display_name.charAt(0).toUpperCase() : 
                        (conversation.name ? conversation.name.charAt(0).toUpperCase() : '?'));
                
                avatarHtml = `<div class="dashboard-conversation-avatar-text">${initial}</div>`;
            }
            
            // Nombre a mostrar
            const displayName = conversation.is_group ? 
                conversation.name : 
                (conversation.other_user ? conversation.other_user.display_name : conversation.name);
            
            // Último mensaje
            const lastMessagePreview = conversation.last_message ? 
                ((conversation.last_message.is_mine ? 'Tú: ' : '') + conversation.last_message.content) : 
                'Sin mensajes';
            
            // Crear elemento HTML
            html += `
                <div class="dashboard-conversation-item ${activeRoomId === conversation.id ? 'active' : ''}" data-room-id="${conversation.id}">
                    <div class="dashboard-conversation-avatar">
                        ${avatarHtml}
                    </div>
                    <div class="dashboard-conversation-details">
                        <div class="dashboard-conversation-name">${displayName}</div>
                        <div class="dashboard-conversation-preview">${lastMessagePreview}</div>
                    </div>
                    <div class="dashboard-conversation-meta">
                        ${conversation.last_message ? 
                            `<div class="dashboard-conversation-time">${formatMessageTime(conversation.last_message.created_at)}</div>` : 
                            ''}
                        ${conversation.unread_count > 0 ? 
                            `<div class="dashboard-conversation-unread">${conversation.unread_count}</div>` : 
                            ''}
                    </div>
                </div>
            `;
        });
        
        dashboardConversationsList.innerHTML = html;
        
        // Agregar event listeners a los ítems de conversación
        document.querySelectorAll('.dashboard-conversation-item').forEach(item => {
            item.addEventListener('click', function() {
                const roomId = this.getAttribute('data-room-id');
                openConversation(roomId);
                
                // Marcar como activa esta conversación
                document.querySelectorAll('.dashboard-conversation-item').forEach(el => {
                    el.classList.remove('active');
                });
                this.classList.add('active');
                
                // Remover badge de no leídos
                const unreadBadge = this.querySelector('.dashboard-conversation-unread');
                if (unreadBadge) {
                    unreadBadge.remove();
                }
            });
        });
    }
    
    /**
     * Busca conversaciones por término
     */
    function searchConversations(query) {
        if (!dashboardConversationsList) return;
        
        query = query.toLowerCase();
        
        // Filtrar conversaciones localmente
        const filteredConversations = conversations.filter(conversation => {
            const name = conversation.is_group ? 
                conversation.name : 
                (conversation.other_user ? conversation.other_user.display_name : conversation.name);
            
            return name.toLowerCase().includes(query);
        });
        
        renderConversations(filteredConversations);
    }
    
    /**
     * Busca usuarios por nombre o email
     */
    function searchUsers(query) {
        if (!dashboardChatUserResults) return;
        
        // Mostrar indicador de carga
        dashboardChatUserResults.innerHTML = `
            <div class="chat-loading">
                <i class="fas fa-spinner fa-spin"></i> Buscando usuarios...
            </div>
        `;
        
        fetch(`/chat/api/buscar-usuarios/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.users.length > 0) {
                    let html = '';
                    
                    data.users.forEach(user => {
                        let avatarHtml = '';
                        
                        if (user.profile_picture) {
                            avatarHtml = `<img src="${user.profile_picture}" alt="${user.full_name}">`;
                        } else {
                            // Usar la primera letra del nombre o del email
                            const initial = user.full_name ? user.full_name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase();
                            avatarHtml = `<div class="dashboard-chat-user-text">${initial}</div>`;
                        }
                        
                        html += `
                            <div class="dashboard-chat-user-item" data-user-id="${user.id}">
                                <div class="dashboard-chat-user-avatar">
                                    ${avatarHtml}
                                </div>
                                <div class="dashboard-chat-user-name">${user.full_name}</div>
                            </div>
                        `;
                    });
                    
                    dashboardChatUserResults.innerHTML = html;
                    
                    // Agregar event listeners
                    document.querySelectorAll('.dashboard-chat-user-item').forEach(item => {
                        item.addEventListener('click', function() {
                            const userId = this.getAttribute('data-user-id');
                            createNewConversation(userId);
                        });
                    });
                } else {
                    dashboardChatUserResults.innerHTML = `
                        <div class="p-3 text-center text-muted">
                            No se encontraron usuarios con "${query}"
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error al buscar usuarios:', error);
                dashboardChatUserResults.innerHTML = `
                    <div class="p-3 text-center text-muted">
                        Error al buscar usuarios
                    </div>
                `;
            });
    }
    
    /**
     * Crea una nueva conversación con un usuario
     */
    function createNewConversation(userId) {
        fetch('/chat/api/crear-chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Cerrar modal
                $(dashboardNewChatModal).modal('hide');
                
                // Cargar conversaciones y abrir la nueva
                loadConversations();
                setTimeout(() => {
                    openConversation(data.room_id);
                }, 500);
            } else {
                alert('Error al crear la conversación: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al crear la conversación');
        });
    }
    
    /**
     * Abre una conversación específica
     */
    function openConversation(roomId) {
        if (!dashboardChatEmpty || !dashboardChatConversation || !dashboardChatMessages) return;
        
        // Guardar ID de sala activa
        activeRoomId = roomId;
        
        // Mostrar panel de conversación
        dashboardChatEmpty.style.display = 'none';
        dashboardChatConversation.style.display = 'flex';
        
        // Mostrar loading en el contenedor de mensajes
        dashboardChatMessages.innerHTML = `
            <div class="chat-loading">
                <i class="fas fa-spinner fa-spin"></i> Cargando mensajes...
            </div>
        `;
        
        // Cargar información de la sala
        loadRoomInfo(roomId);
        
        // Cargar mensajes
        loadMessages(roomId);
        
        // Configurar intervalo de actualización
        if (messagesUpdateInterval) {
            clearInterval(messagesUpdateInterval);
        }
        
        messagesUpdateInterval = setInterval(() => {
            updateMessages(roomId);
        }, 5000);
    }
    
    /**
     * Carga la información de una sala
     */
    function loadRoomInfo(roomId) {
        const headerTitle = document.querySelector('.conversation-name');
        const headerAvatar = document.querySelector('.conversation-avatar');
        
        if (!headerTitle || !headerAvatar) return;
        
        fetch(`/chat/api/sala-info/?room_id=${roomId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Actualizar título
                    headerTitle.textContent = data.room.name;
                    
                    // Actualizar avatar
                    if (data.room.profile_pic_url) {
                        headerAvatar.innerHTML = `<img src="${data.room.profile_pic_url}" alt="${data.room.name}">`;
                    } else {
                        headerAvatar.innerHTML = data.room.is_group ? 
                            '<i class="fas fa-users"></i>' : 
                            `<span>${data.room.name.charAt(0).toUpperCase()}</span>`;
                    }
                }
            })
            .catch(error => {
                console.error('Error al cargar info de sala:', error);
            });
    }
    
    /**
     * Carga los mensajes de una sala
     */
    function loadMessages(roomId) {
        if (!dashboardChatMessages) return;
        
        fetch(`/chat/api/mensajes/${roomId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    renderMessages(data.messages);
                    
                    // Scroll al final
                    dashboardChatMessages.scrollTop = dashboardChatMessages.scrollHeight;
                    
                    // Actualizar lista de conversaciones para quitar badge de no leídos
                    updateActiveConversation();
                } else {
                    dashboardChatMessages.innerHTML = `
                        <div class="p-3 text-center text-muted">
                            Error al cargar los mensajes
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error al cargar mensajes:', error);
                dashboardChatMessages.innerHTML = `
                    <div class="p-3 text-center text-muted">
                        Error al cargar los mensajes
                    </div>
                `;
            });
    }
    
    /**
     * Renderiza los mensajes en el contenedor
     */
    function renderMessages(messages) {
        if (!dashboardChatMessages) return;
        
        if (!messages || messages.length === 0) {
            dashboardChatMessages.innerHTML = `
                <div class="p-3 text-center text-muted">
                    No hay mensajes en esta conversación
                </div>
            `;
            return;
        }
        
        let html = '';
        let previousDate = null;
        
        messages.forEach(message => {
            // Verificar si debemos mostrar separador de fecha
            const messageDate = new Date(message.created_at);
            const formattedDate = formatMessageDate(messageDate);
            
            if (!previousDate || formatMessageDate(new Date(previousDate)) !== formattedDate) {
                html += `
                    <div class="dashboard-chat-date-separator">
                        <span>${formattedDate}</span>
                    </div>
                `;
                previousDate = message.created_at;
            }
            
            // Preparar avatar para mensajes entrantes
            let avatarHtml = '';
            if (!message.is_mine && message.sender) {
                if (message.sender.profile_pic_url) {
                    avatarHtml = `<div class="message-avatar"><img src="${message.sender.profile_pic_url}" alt="${message.sender.name}"></div>`;
                } else {
                    avatarHtml = `<div class="message-avatar"><div class="message-avatar-text">${message.sender.name.charAt(0).toUpperCase()}</div></div>`;
                }
            }
            
            // Preparar contenido del mensaje según su tipo
            let messageContent = '';
            
            if (message.message_type === 'image') {
                // Si tiene contenido de texto, mostrarlo
                if (message.content) {
                    messageContent += `<div>${message.content.replace(/\n/g, '<br>')}</div>`;
                }
                
                // Mostrar la imagen
                if (message.image_url) {
                    messageContent += `<img src="${message.image_url}" alt="Imagen" class="message-image">`;
                }
            } else {
                // Mensaje de texto normal
                messageContent = message.content.replace(/\n/g, '<br>');
            }
            
            // Crear HTML del mensaje
            html += `
                <div class="dashboard-chat-message ${message.is_mine ? 'outgoing' : 'incoming'}" data-message-id="${message.id}">
                    ${!message.is_mine ? avatarHtml : ''}
                    <div class="message-bubble">
                        ${messageContent}
                        <div class="message-time">${formatMessageTime(message.created_at)}</div>
                    </div>
                </div>
            `;
        });
        
        dashboardChatMessages.innerHTML = html;
    }
    
    /**
     * Actualiza los mensajes, cargando solo los nuevos
     */
    function updateMessages(roomId) {
        if (!dashboardChatMessages || activeRoomId !== roomId) return;
        
        // Obtener ID del último mensaje
        const messages = dashboardChatMessages.querySelectorAll('.dashboard-chat-message');
        let lastId = 0;
        
        if (messages.length > 0) {
            const lastMessage = messages[messages.length - 1];
            lastId = lastMessage.getAttribute('data-message-id');
        }
        
        // Obtener nuevos mensajes
        fetch(`/chat/api/mensajes/${roomId}/?last_id=${lastId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.messages && data.messages.length > 0) {
                    // Eliminar mensaje de "no hay mensajes" si existe
                    const emptyMessage = dashboardChatMessages.querySelector('.text-muted');
                    if (emptyMessage) {
                        dashboardChatMessages.innerHTML = '';
                    }
                    
                    let html = '';
                    data.messages.forEach(message => {
                        // Preparar avatar para mensajes entrantes
                        let avatarHtml = '';
                        if (!message.is_mine && message.sender) {
                            if (message.sender.profile_pic_url) {
                                avatarHtml = `<div class="message-avatar"><img src="${message.sender.profile_pic_url}" alt="${message.sender.name}"></div>`;
                            } else {
                                avatarHtml = `<div class="message-avatar"><div class="message-avatar-text">${message.sender.name.charAt(0).toUpperCase()}</div></div>`;
                            }
                        }
                        
                        // Preparar contenido del mensaje según su tipo
                        let messageContent = '';
                        
                        if (message.message_type === 'image') {
                            // Si tiene contenido de texto, mostrarlo
                            if (message.content) {
                                messageContent += `<div>${message.content.replace(/\n/g, '<br>')}</div>`;
                            }
                            
                            // Mostrar la imagen
                            if (message.image_url) {
                                messageContent += `<img src="${message.image_url}" alt="Imagen" class="message-image">`;
                            }
                        } else {
                            // Mensaje de texto normal
                            messageContent = message.content.replace(/\n/g, '<br>');
                        }
                        
                        // Crear HTML del mensaje
                        html += `
                            <div class="dashboard-chat-message ${message.is_mine ? 'outgoing' : 'incoming'}" data-message-id="${message.id}">
                                ${!message.is_mine ? avatarHtml : ''}
                                <div class="message-bubble">
                                    ${messageContent}
                                    <div class="message-time">${formatMessageTime(message.created_at)}</div>
                                </div>
                            </div>
                        `;
                    });
                    
                    // Añadir nuevos mensajes
                    dashboardChatMessages.insertAdjacentHTML('beforeend', html);
                    
                    // Scroll al final
                    dashboardChatMessages.scrollTop = dashboardChatMessages.scrollHeight;
                    
                    // Actualizar lista de conversaciones
                    loadConversations();
                }
            })
            .catch(error => {
                console.error('Error al actualizar mensajes:', error);
            });
    }
    
    /**
     * Envía un mensaje en la conversación activa
     */
    function sendMessage() {
        if (!activeRoomId) return;
        
        const content = dashboardChatMessageInput ? dashboardChatMessageInput.value.trim() : '';
        
        // Si no hay contenido ni imagen, no enviar nada
        if (!content && !selectedImage) return;
        
        // Deshabilitar input mientras se envía
        if (dashboardChatMessageInput) {
            dashboardChatMessageInput.disabled = true;
        }
        
        // Preparar datos para enviar
        if (selectedImage) {
            // Enviar con FormData para la imagen
            const formData = new FormData();
            formData.append('content', content);
            formData.append('image', selectedImage);
            
            fetch(`/chat/api/enviar/${activeRoomId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                },
                body: formData
            })
            .then(response => response.json())
            .then(handleSendMessageResponse)
            .catch(handleSendMessageError);
        } else {
            // Enviar como JSON para mensaje de texto
            fetch(`/chat/api/enviar/${activeRoomId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({ content })
            })
            .then(response => response.json())
            .then(handleSendMessageResponse)
            .catch(handleSendMessageError);
        }
    }
    
    /**
     * Maneja la respuesta del envío de mensajes
     */
    function handleSendMessageResponse(data) {
        // Habilitar input
        if (dashboardChatMessageInput) {
            dashboardChatMessageInput.disabled = false;
        }
        
        if (data.status === 'success') {
            // Limpiar input y vista previa de imagen
            if (dashboardChatMessageInput) {
                dashboardChatMessageInput.value = '';
                dashboardChatMessageInput.style.height = 'auto';
            }
            clearSelectedImage();
            
            // Actualizar mensajes
            updateMessages(activeRoomId);
        } else {
            alert('Error al enviar el mensaje: ' + data.message);
        }
    }
    
    /**
     * Maneja errores en el envío de mensajes
     */
    function handleSendMessageError(error) {
        console.error('Error al enviar mensaje:', error);
        alert('Error al enviar el mensaje');
        
        // Habilitar input
        if (dashboardChatMessageInput) {
            dashboardChatMessageInput.disabled = false;
        }
    }
    
    /**
     * Actualiza la visualización de la conversación activa
     */
    function updateActiveConversation() {
        // Marcar la conversación activa en la lista y quitar badge de no leídos
        document.querySelectorAll('.dashboard-conversation-item').forEach(item => {
            const roomId = item.getAttribute('data-room-id');
            if (roomId === activeRoomId) {
                item.classList.add('active');
                const unreadBadge = item.querySelector('.dashboard-conversation-unread');
                if (unreadBadge) {
                    unreadBadge.remove();
                }
            } else {
                item.classList.remove('active');
            }
        });
    }
    
    /**
     * Formatea la fecha de un mensaje para los separadores
     */
    function formatMessageDate(date) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        if (date >= today) {
            return 'Hoy';
        } else if (date >= yesterday) {
            return 'Ayer';
        } else {
            return date.toLocaleDateString('es-ES', { 
                day: 'numeric', 
                month: 'long', 
                year: 'numeric' 
            });
        }
    }
    
    /**
     * Formatea la hora de un mensaje
     */
    function formatMessageTime(isoDate) {
        const date = new Date(isoDate);
        return date.toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }
    
    /**
     * Obtiene el token CSRF de las cookies
     */
    function getCsrfToken() {
        // Primero intentar obtener el token de un input o meta tag
        let token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                   document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        
        // Si no se encuentra, buscarlo en las cookies (método más confiable para Django)
        if (!token) {
            token = getCookie('csrftoken');
        }
        
        return token || '';
    }
    
    /**
     * Función auxiliar para obtener valores de cookies
     */
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
    
    /**
     * Carga usuarios sugeridos para iniciar una conversación
     */
    function loadSuggestedUsers() {
        if (!dashboardChatUserResults) return;
        
        fetch('/chat/api/usuarios-sugeridos/')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.users.length > 0) {
                    let html = '';
                    
                    data.users.forEach(user => {
                        let avatarHtml = '';
                        
                        if (user.profile_picture) {
                            avatarHtml = `<img src="${user.profile_picture}" alt="${user.full_name}">`;
                        } else {
                            // Usar la primera letra del nombre o del email
                            const initial = user.full_name ? user.full_name.charAt(0).toUpperCase() : user.email.charAt(0).toUpperCase();
                            avatarHtml = `<div class="dashboard-chat-user-text">${initial}</div>`;
                        }
                        
                        html += `
                            <div class="dashboard-chat-user-item" data-user-id="${user.id}">
                                <div class="dashboard-chat-user-avatar">
                                    ${avatarHtml}
                                </div>
                                <div class="dashboard-chat-user-name">${user.full_name}</div>
                            </div>
                        `;
                    });
                    
                    dashboardChatUserResults.innerHTML = html;
                    
                    // Agregar event listeners
                    document.querySelectorAll('.dashboard-chat-user-item').forEach(item => {
                        item.addEventListener('click', function() {
                            const userId = this.getAttribute('data-user-id');
                            createNewConversation(userId);
                        });
                    });
                } else {
                    dashboardChatUserResults.innerHTML = `
                        <div class="p-3 text-center text-muted">
                            No hay usuarios disponibles
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Error al cargar usuarios sugeridos:', error);
                dashboardChatUserResults.innerHTML = `
                    <div class="p-3 text-center text-muted">
                        Error al cargar usuarios
                    </div>
                `;
            });
    }
}); 