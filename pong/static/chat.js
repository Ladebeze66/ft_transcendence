let chatSockets = {}; // Object to hold WebSockets for multiple chat rooms

async function initializeChat(userId, roomName) {
    console.log('Initialisation du chat pour userId:', userId);

    const playerData = await fetchPlayerData(userId);
    if (playerData) {
        console.log('Données du joueur récupérées:', playerData);

        // Affichage du nom d'utilisateur et du rang dans le chat
        const chatHeader = document.getElementById('chat-header');
        chatHeader.innerText = `Chat - ${playerData.name} (Rang: ${playerData.rank})`;

        // Affichage des statistiques du joueur
        const playerStats = document.getElementById('player-stats');
        playerStats.innerHTML = `
            <p>Total de matchs: ${playerData.total_matches}</p>
            <p>Total de victoires: ${playerData.total_wins}</p>
        `;

        // Initialiser le WebSocket pour le chat de la room spécifiée
        if (chatSockets[roomName]) {
            chatSockets[roomName].close();
        }
        const chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/${roomName}/`);

        chatSocket.onopen = function (event) {
            console.log(`Connexion WebSocket pour le chat établie pour la room: ${roomName}`);
            chatSocket.send(JSON.stringify({
                message: `User has joined the chat`,
                username: playerData.name
            }));
        };

        chatSocket.onmessage = function (event) {
            const data = JSON.parse(event.data);
            const message = data.message;
            const username = data.username;
            const chatMessages = document.getElementById(`chat-messages-${roomName}`);
            chatMessages.innerHTML += `<p><strong>${username}:</strong> ${message}</p>`;
        };

        chatSocket.onclose = function (event) {
            console.log(`Connexion WebSocket pour le chat fermée pour la room: ${roomName}`);
        };

        chatSocket.onerror = function (error) {
            console.error(`Erreur WebSocket pour la room: ${roomName}`, error);
            // Tentative de reconnexion après 5 secondes
            setTimeout(() => initializeChat(userId, roomName), 5000);
        };

        chatSockets[roomName] = chatSocket;

        // Gestion de l'envoi des messages pour cette room
        const sendMessageButton = document.getElementById(`send-message-button-${roomName}`);
        const messageInput = document.getElementById(`message-input-${roomName}`);

        sendMessageButton.addEventListener('click', function() {
            const message = messageInput.value.trim();
            if (message !== '') {
                chatSocket.send(JSON.stringify({
                    'message': message,
                    'username': playerData.name
                }));
                const chatMessages = document.getElementById(`chat-messages-${roomName}`);
                chatMessages.innerHTML += `<p><strong>${playerData.name}:</strong> ${message}</p>`;
                messageInput.value = '';  // Effacer le champ de saisie
            }
        });

        console.log('Chat initialisé avec succès pour:', playerData.name, 'dans la room:', roomName);
    } else {
        console.error('Impossible de récupérer les données du joueur pour userId:', userId);
        alert('Impossible de récupérer les données du joueur');
    }
}

function startChatAfterLogin(userId) {
    console.log('Démarrage des fonctions après connexion pour l\'utilisateur:', userId);

    // Initialiser le chat pour la room principale
    initializeChat(userId, 'main_room');

    // Initialiser le chat pour la room de sélection de jeu
    initializeChat(userId, 'game_room_1');

    // Placez ici d'autres fonctions ou initialisations nécessaires à l'avenir
    initializeOtherFeatures(userId);
}
