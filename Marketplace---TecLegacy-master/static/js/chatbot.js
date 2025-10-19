document.addEventListener('DOMContentLoaded', function() {
    const chatbotToggle = document.querySelector('.chatbot-toggle');
    const chatbotContainer = document.querySelector('.chatbot-container');
    const chatbotClose = document.querySelector('.chatbot-close');
    const chatbotMessages = document.querySelector('.chatbot-messages');
    const chatbotInput = document.querySelector('.chatbot-input input');
    const chatbotSendBtn = document.querySelector('.chatbot-input button');

    // Alternar visibilidad del chatbot
    chatbotToggle.addEventListener('click', function() {
        chatbotContainer.classList.toggle('d-none');
        chatbotInput.focus();
    });

    // Cerrar chatbot
    chatbotClose.addEventListener('click', function() {
        chatbotContainer.classList.add('d-none');
    });

    // Mostrar indicador de escritura
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('chatbot-message', 'bot', 'typing-indicator');
        typingDiv.innerHTML = '<span></span><span></span><span></span>';
        chatbotMessages.appendChild(typingDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        return typingDiv;
    }

    // Enviar mensaje
    function sendMessage() {
        const message = chatbotInput.value.trim();
        if (message === '') return;

        // Añadir mensaje del usuario a la interfaz
        appendMessage('user', message);
        chatbotInput.value = '';

        // Mostrar indicador de escritura
        const typingIndicator = showTypingIndicator();

        // Enviar consulta al servidor
        fetch('/chatbot/query/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                query: message
            })
        })
        .then(response => response.json())
        .then(data => {
            // Eliminar indicador de escritura
            typingIndicator.remove();

            if (data.success) {
                // Añadir la respuesta del chatbot
                appendMessage('bot', data.response);

                // Hacer los enlaces clicables
                const links = chatbotMessages.querySelectorAll('.bot a');
                links.forEach(link => {
                    link.addEventListener('click', function(e) {
                        // Opcional: cerrar el chatbot al hacer clic en un enlace
                        // chatbotContainer.classList.add('d-none');
                    });
                });
            } else {
                appendMessage('bot', 'No lo siento pero ha ocurrido un error. Inténtalo de nuevo más tarde que le quedan como 60 años.');
            }

            // Scroll al final de los mensajes
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        })
        .catch(error => {
            console.error('Error:', error);
            typingIndicator.remove();
            appendMessage('bot', 'Lo siento, ha ocurrido un error de conexión. Inténtalo de nuevo más tarde o preguntar a arle.');
            chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
        });
    }

    // Añadir mensaje a la interfaz
    function appendMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chatbot-message', sender);
        messageDiv.innerHTML = message;
        chatbotMessages.appendChild(messageDiv);
        chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
    }

    // Eventos para enviar mensajes
    chatbotSendBtn.addEventListener('click', sendMessage);
    chatbotInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Añadir estilos para el indicador de escritura
    const style = document.createElement('style');
    style.textContent = `
        .typing-indicator {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 10px 15px;
        }
        .typing-indicator span {
            height: 8px;
            width: 8px;
            background: #fff;
            border-radius: 50%;
            margin: 0 3px;
            display: inline-block;
            animation: typing 1.5s infinite;
        }
        .typing-indicator span:nth-child(2) {
            animation-delay: 0.3s;
        }
        @keyframes typing {
            0%, 6%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }
    `;
    document.head.appendChild(style);

    // Mensaje de bienvenida inicial (opcional)
    setTimeout(() => {
        appendMessage('bot', '¡Hola! Soy el asistente y mascota de TecLegacy Juanjo. ¿En qué puedo ayudarte hoy? Puedes preguntarme por productos gaming o servicios privados en persona.');
    }, 500);
});