export default function chat(prop={}) {
    let websocket = undefined;  // Déclaration de la variable websocket
    let yourName = undefined;

    // Code pré-rendu (par exemple, fetch request)
    let prerender = async () => {
        const me_response = await fetchMod(`/api/me`);
        if (!me_response.ok) {
            history.back();
            return false;
        }
        let value = await me_response.json();
        yourName = value.username;

        const response = await fetchMod(`/api/player/${yourName}/friends`, { method: "GET" });
        if (!response.ok) {
            history.back();
            return false;
        }

        value = await response.json();
        prop.friendList = value;

        const blockedResponse = await fetchMod(`/api/player/${yourName}/blocked`, { method: "GET" });
        if (!blockedResponse.ok) {
            history.back();
            return false;
        }

        value = await blockedResponse.json();
        prop.blockList = value;

        // Initialiser le WebSocket une fois que le pré-rendu est terminé
        websocket = new WebSocket(`ws://${window.location.host}/ws/chat/${prop.roomid}/`);

        // Listener pour les messages entrants
        websocket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log(data);
            // Ajoutez ici la logique pour afficher les messages dans l'interface utilisateur
        };

        // Listener pour la fermeture de la connexion
        websocket.onclose = function(event) {
            console.log('WebSocket connection closed:', event);
        };

        return true; // Retourne true pour continuer vers render_code
    }

    // Code HTML à retourner
    let render_code = () => {
        return `
        <h1 class="title">Chat</h1>
        <div class="d-flex flex-grow-1 align-self-stretch overflow-hidden" id='contentDiv'>
            <div class="d-flex flex-column friend-list p-3">
                <h4>Friends</h4>
                <div dir="rtl" class="d-flex flex-column flex-grow-1 overflow-y-auto" style="padding-left:5px;" id="friend-list-items"></div>
            </div>
            <div class="d-flex flex-column flex-grow-1 px-2">
                <div class="chat-content-field d-flex flex-column-reverse flex-grow-1 p-2 mb-2 overflow-y-auto rounded" id="chatContentField"></div>
                <div class="text-input-box">
                    <div class="d-flex flex-row text-input-box">
                        <textarea class="form-control" rows="1" placeholder="Type your message here..." id="dataEnter"></textarea>
                        <button type="button" class="btn btn-dark mx-2 disabled" id="sendMessageButton">Send</button>
                        <button type="button" class="btn btn-dark d-flex disabled gap-3" id="inviteForMatchButton">
                            Invite
                            <select class='rounded bg-black border-black text-white' id="inviteForMatchType">
                                <option value="pong">Pong</option>
                                <option value="apong">APong Us</option>
                            </select>
                        </button>
                    </div>
                </div>
            </div>
        </div>
        `;
    }

    // Attacher tous les listeners d'événements ici
    let postrender = () => {
        const friendList = document.getElementById("friend-list-items");
        const chatContentField = document.getElementById("chatContentField");
        const sendMessageButton = document.getElementById('sendMessageButton');
        const sendInviteButton = document.getElementById('inviteForMatchButton');

        // Envoyer un message via le WebSocket lorsque l'utilisateur clique sur le bouton d'envoi
        sendMessageButton.onclick = () => {
            const messageInputDom = document.getElementById('dataEnter');
            const message = messageInputDom.value;
            websocket.send(JSON.stringify({
                'message': message
            }));
            messageInputDom.value = '';  // Efface le champ de saisie après l'envoi
        };

        // Ajouter d'autres listeners d'événements et la logique ici
    }

    return [prerender, render_code, postrender];
}
