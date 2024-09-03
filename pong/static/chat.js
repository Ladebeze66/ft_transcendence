	// Initialisation du chat WebSocket
	function startChatWebSocket(token) {
    	console.log("Initializing chat WebSocket...");

    	chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/`);

    	chatSocket.onopen = function () {
        	console.log('Chat WebSocket connection established');
        	// Envoi du token pour authentification dès l'ouverture de la connexion
        	chatSocket.send(JSON.stringify({
            	'type': 'authenticate',
            	'token': token
        	}));
    	};

    	chatSocket.onmessage = function (event) {
        	const data = JSON.parse(event.data);
        	if (data.type === 'authenticated') {
            	console.log('User authenticated for chat successfully');
        	} else if (data.message) {
            	const message = data.message;
            	const chatLog = document.getElementById('chat-log');
            	const messageElement = document.createElement('div');
            	messageElement.textContent = message;
            	chatLog.appendChild(messageElement);
        	} else {
            	console.warn('Unhandled message type:', data);
        	}
    	};

    	chatSocket.onclose = function (event) {
        	if (event.wasClean) {
            	console.log(`Chat WebSocket closed cleanly, code=${event.code}, reason=${event.reason}`);
        	} else {
            	console.error('Chat WebSocket closed unexpectedly');
        	}
    	};

    	chatSocket.onerror = function (error) {
        	console.error('Chat WebSocket error:', error);
    	};

    	const chatInput = document.getElementById('chat-input');
    	const chatButton = document.getElementById('chat-button');

    	chatButton.addEventListener('click', () => {
        	const message = chatInput.value.trim();
        	if (message) {
            	console.log("Sending chat message:", message);
            	chatSocket.send(JSON.stringify({ 'message': message, 'username': username }));
            	chatInput.value = '';
        	}
    	});

    	chatInput.addEventListener('keypress', function (event) {
        	if (event.key === 'Enter') {
            	chatButton.click();
        	}
    	});
	}