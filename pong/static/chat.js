// Fonction pour récupérer les données du joueur
async function fetchPlayerData(userId) {
    try {
        const response = await fetch(`/player_data/${userId}/`);
        if (!response.ok) {
            throw new Error('Erreur lors de la récupération des données du joueur');
        }
        const playerData = await response.json();
        return playerData;
    } catch (error) {
        console.error('Erreur:', error);
        return null;
    }
}

// Initialisation du chat avec les données du joueur et WebSocket
async function initializeChat(userId) {
    const playerData = await fetchPlayerData(userId);
    if (playerData) {
        // Affichage du nom d'utilisateur et du rang dans le chat
        const chatHeader = document.getElementById('chat-header');
        chatHeader.innerText = `Chat - ${playerData.username} (Rang: ${playerData.rank})`;

        // Affichage des statistiques du joueur
        const playerStats = document.getElementById('player-stats');
        playerStats.innerHTML = `
            <p>Total de matchs: ${playerData.total_matches}</p>
            <p>Total de victoires: ${playerData.total_wins}</p>
        `;

        // Logique pour gérer les messages du chat (exemple de base)
        const sendMessageButton = document.getElementById('send-message-button');
        const messageInput = document.getElementById('message-input');
        const chatMessages = document.getElementById('chat-messages');

        // Création de la connexion WebSocket
        const chatSocket = new WebSocket(
            `ws://${window.location.host}/ws/chat/${userId}/`
        );

        // Recevoir des messages via WebSocket
        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            chatMessages.innerHTML += `<p><strong>${data.username}:</strong> ${data.message}</p>`;
        };

        // Gestion de l'erreur WebSocket
        chatSocket.onerror = function(e) {
            console.error('WebSocket error observed:', e);
        };

        // Envoyer un message via WebSocket
        sendMessageButton.addEventListener('click', function() {
            const message = messageInput.value;
            if (message.trim() !== '') {
                chatSocket.send(JSON.stringify({
                    'message': message,
                    'username': playerData.username
                }));
                messageInput.value = '';  // Effacer le champ de saisie
            }
        });

    } else {
        // Gestion de l'erreur si les données du joueur ne sont pas disponibles
        alert('Impossible de récupérer les données du joueur');
    }
}

// Appeler cette fonction après l'authentification de l'utilisateur
function startChatAfterLogin(userId) {
    initializeChat(userId);
}
