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

async function initializeChat(userId) {
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

        // Initialiser le WebSocket pour le chat
        const chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/${playerData.name}/`);

        chatSocket.onopen = function (event) {
            console.log('Connexion WebSocket pour le chat établie');
        };

        chatSocket.onmessage = function (event) {
            const data = JSON.parse(event.data);
            const message = data.message;
            const username = data.username;
            const chatMessages = document.getElementById('chat-messages');
            chatMessages.innerHTML += `<p><strong>${username}:</strong> ${message}</p>`;
        };

        chatSocket.onclose = function (event) {
            console.log('Connexion WebSocket pour le chat fermée');
        };

        // Gestion de l'envoi des messages
        const sendMessageButton = document.getElementById('send-message-button');
        const messageInput = document.getElementById('message-input');

        sendMessageButton.addEventListener('click', function() {
            const message = messageInput.value;
            if (message.trim() !== '') {
                chatSocket.send(JSON.stringify({
                    'message': message,
                    'username': playerData.name
                }));
                chatMessages.innerHTML += `<p><strong>${playerData.name}:</strong> ${message}</p>`;
                messageInput.value = '';  // Effacer le champ de saisie
            }
        });

        console.log('Chat initialisé avec succès pour:', playerData.name);
    } else {
        console.error('Impossible de récupérer les données du joueur pour userId:', userId);
        alert('Impossible de récupérer les données du joueur');
    }
}

// Appelée après l'authentification réussie de l'utilisateur
function startChatAfterLogin(userId) {
    console.log('Démarrage des fonctions après connexion pour l\'utilisateur:', userId);

    // Initialiser le chat
    initializeChat(userId);

    // Placez ici d'autres fonctions ou initialisations nécessaires à l'avenir
    // Par exemple, vous pourriez vouloir initialiser des notifications, charger des données spécifiques, etc.
    initializeOtherFeatures(userId);
}