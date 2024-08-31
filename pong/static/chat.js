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
	console.log('Initialisation du chat pour userId:', userId); // Log pour vérifier l'ID utilisateur

	const playerData = await fetchPlayerData(userId);
	if (playerData) {
		console.log('Données du joueur récupérées:', playerData); // Log les données du joueur récupérées

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

		sendMessageButton.addEventListener('click', function() {
			const message = messageInput.value;
			if (message.trim() !== '') {
				chatMessages.innerHTML += `<p><strong>${playerData.username}:</strong> ${message}</p>`;
				messageInput.value = '';  // Effacer le champ de saisie
			}
		});

		console.log('Chat initialisé avec succès pour:', playerData.username); // Log la fin du processus d'initialisation du chat
	} else {
		console.error('Impossible de récupérer les données du joueur pour userId:', userId); // Log en cas d'échec de récupération des données
		alert('Impossible de récupérer les données du joueur');
	}
}

// Appeler cette fonction après l'authentification de l'utilisateur
function startChatAfterLogin(userId) {
	initializeChat(userId);
}
