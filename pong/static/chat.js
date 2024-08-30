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

// Initialisation du chat avec les données du joueur
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

        sendMessageButton.addEventListener('click', function() {
            const message = messageInput.value;
            if (message.trim() !== '') {
                chatMessages.innerHTML += `<p><strong>${playerData.username}:</strong> ${message}</p>`;
                messageInput.value = '';  // Effacer le champ de saisie
            }
        });
    } else {
        // Gestion de l'erreur si les données du joueur ne sont pas disponibles
        alert('Impossible de récupérer les données du joueur');
    }
}

// Appeler la fonction avec l'ID de l'utilisateur connecté
const userId = 1; // Remplace ceci par l'ID réel de l'utilisateur connecté
initializeChat(userId);
