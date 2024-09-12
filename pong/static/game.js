document.addEventListener('DOMContentLoaded', () => {
	console.log("DOM fully loaded and parsed");
	const formBlock = document.getElementById('block-form');

	const authForm = document.getElementById('auth-form');
	const nicknameInput = document.getElementById('nickname');
	const checkNicknameButton = document.getElementById('check-nickname');

	const registerForm = document.getElementById('register-form');
	const passwordInput = document.getElementById('password');
	const confirmPasswordInput = document.getElementById('confirm-password');
	const registerButton = document.getElementById('register');

	const loginForm = document.getElementById('login-form');
	const loginPasswordInput = document.getElementById('login-password');
	const loginButton = document.getElementById('login');

	const authForm2 = document.getElementById('auth-form2');
	const nicknameInput2 = document.getElementById('nickname2');
	const checkNicknameButton2 = document.getElementById('check-nickname2');

	const registerForm2 = document.getElementById('register-form2');
	const passwordInput2 = document.getElementById('password2');
	const confirmPasswordInput2 = document.getElementById('confirm-password2');
	const registerButton2 = document.getElementById('register2');

	const loginForm2 = document.getElementById('login-form2');
	const loginPasswordInput2 = document.getElementById('login-password2');
	const loginButton2 = document.getElementById('login2');

	const gameContainer = document.getElementById('game1');
	const tournamentContainer = document.getElementById('tournament-bracket');

	const pongElements = document.getElementById('pong-elements');
	const logo = document.querySelector('.logo');

	const localGameButton = document.getElementById('local-game');
	const quickMatchButton = document.getElementById('quick-match');
	const tournamentButton = document.getElementById('tournament');

	let socket;
	let token;
	let gameState;
	let activeRoom = null;	// Stocker la room active
	let roomSockets = {}; // Stocker les connexions WebSocket par room
	let username; // Ajouter cette variable pour stocker le nom d'utilisateur

	console.log("DOM elements initialized");

	// Auto-focus and key handling for AUTH-FORM
	nicknameInput.focus();
	nicknameInput.addEventListener('keypress', function (event) {
		if (event.key === 'Enter') {
			event.preventDefault();
			handleCheckNickname();  // Appeler directement la fonction au lieu de simuler un clic
		}
	});

	checkNicknameButton.addEventListener('click', handleCheckNickname);
	registerButton.addEventListener('click', handleRegister);
	loginButton.addEventListener('click', handleLogin);

	checkNicknameButton2.addEventListener('click', handleCheckNickname2);
	registerButton2.addEventListener('click', handleRegister2);
	loginButton2.addEventListener('click', handleLogin2);

	localGameButton.addEventListener('click', startLocalGame);
	quickMatchButton.addEventListener('click', startQuickMatch);
	tournamentButton.addEventListener('click', startTournament);

	console.log("Event listeners added");

	// Function to get the CSRF token from cookies
	function getCSRFToken() {
		let csrfToken = null;
		const cookies = document.cookie.split(';');
		cookies.forEach(cookie => {
			const [name, value] = cookie.trim().split('=');
			if (name === 'csrftoken') {
				csrfToken = value;
			}
		});
		return csrfToken;
	}

	async function handleCheckNickname() {
        const nickname = nicknameInput.value.trim();
        if (nickname) {
            try {
                const exists = await checkUserExists(nickname);
                if (exists) {
                    authForm.style.display = 'none';
                    loginForm.style.display = 'block';
                    loginPasswordInput.focus();
                    loginPasswordInput.addEventListener('keypress', function (event) {
                        if (event.key === 'Enter') {
                            event.preventDefault();
                            loginButton.click();
                        }
                    });
                } else {
                    authForm.style.display = 'none';
                    registerForm.style.display = 'block';
                    passwordInput.focus();
                    passwordInput.addEventListener('keypress', function (event) {
                        if (event.key === 'Enter') {
                            confirmPasswordInput.focus();
                            confirmPasswordInput.addEventListener('keypress', function (event) {
                                if (event.key === 'Enter') {
                                    event.preventDefault();
                                    registerButton.click();
                                }
                            });
                        }
                    });
                }
            } catch (error) {
                console.error('Error checking user existence:', error);
            }
        } else {
            alert('Please enter a nickname.');
        }
    }

	async function handleRegister() {
		console.log("handleRegister called");
		const nickname = nicknameInput.value.trim();
		const password = passwordInput.value.trim();
		const confirmPassword = confirmPasswordInput.value.trim();

		// Validation du nom d'utilisateur
		if (!nickname || nickname.length < 3) {
			console.error("Invalid username. It must be at least 3 characters long.");
			alert("Invalid username. It must be at least 3 characters long.");
			return;
		}

		// Validation des mots de passe
		if (password !== confirmPassword) {
			alert('Passwords do not match.');
			console.error('Passwords do not match.');
			return;
		}

		// Tentative d'inscription
		try {
			console.log("Attempting to register user:", nickname);
			const result = await registerUser(nickname, password);

			// Vérification du résultat de l'inscription
			if (result && result.token) {
				token = result.token; // Stocker le token de l'utilisateur
				console.log("Token stored successfully:", token);
				console.log("User registered successfully");

				// Mise à jour de l'interface après inscription réussie
				registerForm.style.display = 'none';
				document.getElementById("post-form-buttons").style.display = 'block';
				username = nickname; // Stocker le nom d'utilisateur

				// Définir le nom de la room principale
				roomName = "main_room";

				// Sécuriser l'appel à `joinRoom` (initialiser le chat WebSocket)
				if (token && roomName) {
					console.log(`Joining room: ${roomName} with token: ${token}`);
					joinRoom(token, roomName, username); // Initialiser le chat WebSocket
				} else {
					console.error("Token or roomName is undefined. Cannot join room.");
					alert("Error joining the chat room. Please try again.");
				}

			} else {
				console.error('Registration failed. Invalid response from server.');
				alert('Registration failed. Please try again.');
			}

		} catch (error) {
			console.error('Error registering user:', error);
			alert('An error occurred during registration. Please try again.');
		}
	}


	async function checkUserExists(username) {
		console.log("checkUserExists called with username:", username);
		try {
			const response = await fetch('/check_user_exists/', {
				method: 'POST',
				headers: {
					'X-CSRFToken': getCSRFToken(),
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username })
			});

			if (!response.ok) {
				console.error(`HTTP error! Status: ${response.status}`);
				return false;
			}

			const data = await response.json();
			console.log("User existence check response:", data);
			return data.exists;
		} catch (error) {
			console.error('Error during user existence check:', error);
			return false;
		}
	}

	async function handleRegister() {
		console.log("handleRegister called");
		const nickname = nicknameInput.value.trim();
		const password = passwordInput.value.trim();
		const confirmPassword = confirmPasswordInput.value.trim();

		if (!nickname || nickname.length < 3) {
			console.error("Invalid username. It must be at least 3 characters long.");
			alert("Invalid username. It must be at least 3 characters long.");
			return;
		}

		if (password === confirmPassword) {
			try {
				console.log("Attempting to register user:", nickname);
				const result = await registerUser(nickname, password);
				if (result) {
					token = result; // Assurez-vous que le token est bien stocké ici
					console.log("Token stored:", token);
					console.log("User registered successfully");
					registerForm.style.display = 'none';
					document.getElementById("post-form-buttons").style.display = 'block';
					username = nickname; // Stocker le nom d'utilisateur après l'inscription
					roomName = "main_room"; // Nom de la room principale
					joinRoom(token,roomName, username); // Initialiser le chat WebSocket
				} else {
					console.error('Registration failed.');
					alert('Registration failed. Please try again.');
				}
			} catch (error) {
				console.error('Error registering user:', error);
			}
		} else {
			alert('Passwords do not match.');
			console.error('Passwords do not match.');
		}
	}

	async function registerUser(username, password) {
		console.log("registerUser called with username:", username);
		try {
			const response = await fetch('/register_user/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username, password })
			});

			if (!response.ok) {
				console.error(`HTTP error! Status: ${response.status}`);
				return null;  // Retournez null en cas d'erreur HTTP
			}

			let data;
			try {
				data = await response.json();
			} catch (error) {
				console.error('Invalid JSON response:', error);
				return null;
			}

			console.log("Registration response data:", data);
			if (data.registered) {
				console.log('User registered successfully:', data);
				return data.token;
			} else {
				console.error('Registration failed:', data.error);
				return null;  // Retournez null si l'enregistrement échoue
			}
		} catch (error) {
			console.error('Error during registration request:', error);
			return null;
		}
	}

	async function handleLogin() {
		console.log("handleLogin called");
		const nickname = nicknameInput.value.trim();
		const password = loginPasswordInput.value.trim();
		try {
			console.log("Attempting to authenticate user:", nickname);
			const result = await authenticateUser(nickname, password);
			if (result) {
				console.log("User authenticated successfully");
				loginForm.style.display = 'none';
				document.getElementById("post-form-buttons").style.display = 'block';
			} else {
				console.error('Authentication failed.');
				alert('Authentication failed. Please try again.');
			}
		} catch (error) {
			console.error('Error authenticating user:', error);
		}
	}

	async function authenticateUser(username, password) {
		console.log("authenticateUser called with username:", username);
		try {
			const response = await fetch('/authenticate_user/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username, password })
			});

			if (!response.ok) {
				console.error(`HTTP error! Status: ${response.status}`);
				return false;
			}

			const data = await response.json();
			console.log("Authentication response data:", data);
			if (data.authenticated) {
				token = data.token;
			}
			return data.authenticated;
		} catch (error) {
			console.error('Error during authentication request:', error);
			return false;
		}
	}


	async function handleCheckNickname2() {
		const nickname2 = nicknameInput2.value.trim();
		if (nickname2) {
			try {
				const exists = await checkUserExists2(nickname2);
				if (exists) {
					authForm2.style.display = 'none';
					loginForm2.style.display = 'block';
					loginPasswordInput2.focus();
					loginPasswordInput2.addEventListener('keypress', function (event) {
						if (event.key === 'Enter') {
							event.preventDefault();
							loginButton2.click();
						}
					});
				} else {
					authForm2.style.display = 'none';
					registerForm2.style.display = 'block';
					passwordInput2.focus();
					passwordInput2.addEventListener('keypress', function (event) {
						if (event.key === 'Enter') {
							confirmPasswordInput2.focus();
							confirmPasswordInput2.addEventListener('keypress', function (event) {
								if (event.key === 'Enter') {
									event.preventDefault();
									registerButton2.click();
								}
							});
						}
					});
				}
			} catch (error) {
				console.error('Error checking user existence:', error);
			}
		} else {
			alert('Please enter a nickname.');
		}
	}

	async function checkUserExists2(username) {
		console.log("checkUserExists2 called with username:", username);
		try {
			const response = await fetch('/check_user_exists/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username })
			});

			if (!response.ok) {
				console.error(`HTTP error! Status: ${response.status}`);
				return false;
			}

			const data = await response.json();
			console.log("User existence check response (checkUserExists2):", data);
			return data.exists;
		} catch (error) {
			console.error('Error during user existence check (checkUserExists2):', error);
			return false;
		}
	}

	async function handleRegister2() {
		console.log("handleRegister2 called");
		const nickname2 = nicknameInput2.value.trim();
		const password2 = passwordInput2.value.trim();
		const confirmPassword2 = confirmPasswordInput2.value.trim();

		if (!nickname2 || nickname2.length < 3) {
			console.error("Invalid username (handleRegister2). It must be at least 3 characters long.");
			alert("Invalid username. It must be at least 3 characters long.");
			return;
		}

		if (password2 === confirmPassword2) {
			try {
				console.log("Attempting to register user (handleRegister2):", nickname2);
				const result = await registerUser2(nickname2, password2);
				if (result) {
					console.log("User registered successfully (handleRegister2)");
					registerForm2.style.display = 'none';
					startLocalGame2();
				} else {
					console.error('Registration failed (handleRegister2).');
					alert('Registration failed. Please try again.');
				}
			} catch (error) {
				console.error('Error registering user (handleRegister2):', error);
			}
		} else {
			alert('Passwords do not match.');
			console.error('Passwords do not match (handleRegister2).');
		}
	}

	async function registerUser2(username, password) {
		console.log("registerUser2 called with username:", username);
		try {
			const response = await fetch('/register_user/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username, password })
			});

			if (!response.ok) {
				console.error(`HTTP error (registerUser2)! Status: ${response.status}`);
				return null;
			}

			let data;
			try {
				data = await response.json();
			} catch (error) {
				console.error('Invalid JSON response (registerUser2):', error);
				return null;
			}

			console.log("Registration response data (registerUser2):", data);
			if (data.registered) {
				console.log('User registered successfully (registerUser2):', data);
				return data.token;
			} else {
				console.error('Registration failed (registerUser2):', data.error);
				return null;
			}
		} catch (error) {
			console.error('Error during registration request (registerUser2):', error);
			return null;
		}
	}

	async function handleLogin2() {
		console.log("handleLogin2 called");
		const nickname2 = nicknameInput2.value.trim();
		const password2 = loginPasswordInput2.value.trim();
		try {
			console.log("Attempting to authenticate user (handleLogin2):", nickname2);
			const result = await authenticateUser2(nickname2, password2);
			if (result) {
				console.log("User authenticated successfully (handleLogin2)");
				loginForm2.style.display = 'none';
				startLocalGame2();
			} else {
				console.error('Authentication failed (handleLogin2).');
				alert('Authentication failed. Please try again.');
			}
		} catch (error) {
			console.error('Error authenticating user (handleLogin2):', error);
		}
	}

	async function authenticateUser2(username, password) {
		console.log("authenticateUser2 called with username:", username);
		try {
			const response = await fetch('/authenticate_user/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ username, password })
			});

			if (!response.ok) {
				console.error(`HTTP error (authenticateUser2)! Status: ${response.status}`);
				return false;
			}

			const data = await response.json();
			console.log("Authentication response data (authenticateUser2):", data);
			if (data.authenticated) {
				token2 = data.token;
			}
			return data.authenticated;
		} catch (error) {
			console.error('Error during authentication request (authenticateUser2):', error);
			return false;
		}
	}

	function startLocalGame() {
		console.log("Starting a Local Game...");

		document.getElementById("post-form-buttons").style.display = 'none';
		console.log("Hid post-form-buttons.");

		authForm2.style.display = 'block';
		console.log("Displayed authForm2.");

		nicknameInput2.focus();
		console.log("Focused on nicknameInput2.");

		nicknameInput2.addEventListener('keypress', function (event) {
			if (event.key === 'Enter') {
				event.preventDefault();
				console.log("Enter key pressed on nicknameInput2.");
				checkNicknameButton2.click();
			}
		});
	}

	function startLocalGame2() {
		console.log("Starting the local game (2 players)...");

		// Display the game container
		gameContainer.style.display = 'flex';
		console.log("Game container set to 'flex'");

		// Hide the logo, pong elements, and form block
		logo.style.display = 'none';
		console.log("Logo hidden");

		pongElements.style.display = 'none';
		console.log("Pong elements hidden");

		formBlock.style.display = 'none';
		console.log("Form block hidden");

		// Log the token before starting the WebSocket connection
		console.log("Token before WebSocket authentication:", token);

		// Check if token is defined
		if (!token) {
			console.error("Token is not defined or is null.");
			return;
		}

		// Start the WebSocket connection
		startWebSocketConnection(token, 2);
		console.log("WebSocket connection initiated for a local game.");
	}

	function startQuickMatch() {
		// Masquer les éléments inutiles et afficher le conteneur de jeu
		gameContainer.style.display = 'flex';
		logo.style.display = 'none';
		pongElements.style.display = 'none';
		formBlock.style.display = 'none';

		// Log pour vérifier le token avant l'authentification WebSocket
		console.log("Token before WebSocket authentication:", token);

		if (!token) {
			console.error("Token is not defined or is null. WebSocket connection aborted.");
			return;
		}

		// Vérification si une connexion WebSocket est déjà active avant d'initialiser
		if (roomSockets["quick_match"] && roomSockets["quick_match"].readyState === WebSocket.OPEN) {
			console.warn("WebSocket for quick_match already open.");
			return;
		}
		//	Rejoindre la room "quick_match"
		roomName = 'quick_match';
		joinRoom(token, roomName, username);
		console.log("Starting WebSocket connection for quick match...");
		startWebSocketConnection(token, 1); // Le "1" pourrait être un identifiant pour le mode Quick Match
	}


    function startTournament() {
		// Masquer les éléments inutiles et afficher le conteneur du tournoi
		tournamentContainer.style.display = 'flex';
		logo.style.display = 'none';
		pongElements.style.display = 'none';
		formBlock.style.display = 'none';

		// Log pour vérifier le token avant l'authentification WebSocket
		console.log("Token before WebSocket authentication:", token);

		if (!token) {
			console.error("Token is not defined or is null. WebSocket connection aborted.");
			return;
		}

		// Vérification si une connexion WebSocket est déjà active avant d'initialiser
		if (roomSockets["tournament"] && roomSockets["tournament"].readyState === WebSocket.OPEN) {
			console.warn("WebSocket for tournament already open.");
			return;
		}
		//	Rejoindre la room "tournament"
		roomName = 'tournament';
		joinRoom(token, roomName, username);
		console.log("Starting WebSocket connection for tournament...");
		startWebSocketConnection(token, 42); // Le "42" pourrait être un identifiant pour le mode tournoi
	}


	function startWebSocketConnection(token, players) {
		if (socket && socket.readyState === WebSocket.OPEN) {
			console.warn('WebSocket connection already open.');
			return;
		}
		socket = new WebSocket(`ws://${window.location.host}/ws/game/`);

		socket.onopen = function (event) {
			console.log('WebSocket connection established');
			if (players === 1) {
				console.log("Sending token for a quick match game");
				socket.send(JSON.stringify({ type: 'authenticate', token: token }));
			} else if (players === 2) {
				console.log("Sending tokens for a local game");
				socket.send(JSON.stringify({ type: 'authenticate2', token_1: token, token_2: token2 }));
			} else {
				console.log("Sending token for a tournament game");
				socket.send(JSON.stringify({ type: 'authenticate3', token: token }));
			}
		};

		// Gestion des messages reçus
		socket.onmessage = function (event) {
			const data = JSON.parse(event.data);
			if (data.type === 'authenticated') {
				console.log('Authentication successful');
			} else if (data.type === 'waiting_room') {
				console.log('Entered the WAITING ROOM');
			} else if (data.type === 'game_start') {
				console.log('Game started:', data.game_id, '(', data.player1, 'vs', data.player2, ')');
				document.addEventListener('keydown', handleKeyDown);
			} else if (data.type === 'game_state_update') {
				updateGameState(data.game_state);
			} else if (data.type === 'player_disconnected') {
				console.log("Player disconnected:", data.player);
			} else if (data.type === 'game_ended') {
				console.log("Game ended:", data.game_id);
			} else if (data.type === 'error') {
				console.error(data.message);
			} else if (data.type === 'update_waiting_room') {
				document.getElementById('tournament-bracket').innerHTML = data.html;
			} else {
				console.log('Message from server:', data.type, data.message);
			}
		};

		// Gestion des fermetures de connexion
		socket.onclose = function (event) {
			console.log('WebSocket connection closed');
		};

		socket.onerror = function (error) {
			console.error('WebSocket error:', error);
		};
	}

	// Gestion des événements de touche
	function handleKeyDown(event) {
		console.log("Key pressed:", event.key);
		if (event.key === 'ArrowUp' || event.key === 'ArrowDown' || event.key === 'w' || event.key === 's') {
			sendKeyPress(event.key.toLowerCase());
		}
	}

	function sendKeyPress(key) {
		console.log("Sending key press:", key);
		if (socket.readyState === WebSocket.OPEN) {
			socket.send(JSON.stringify({ type: 'key_press', key }));
		} else {
			console.warn("WebSocket is not open. Key press not sent.");
		}
	}

	// Fonction pour mettre à jour l'état du jeu
	function updateGameState(newState) {
		console.log("Updating game state...");
		gameState = newState;
		renderGame();
	}

	// Fonction pour rendre l'état du jeu à l'écran
	function renderGame() {
		console.log("Rendering game state...");
		document.getElementById('player1-name').textContent = `${gameState.player1_name}`;
		document.getElementById('player2-name').textContent = `${gameState.player2_name}`;

		document.getElementById('player1-pad').style.top = `${gameState.player1_position}px`;
		document.getElementById('player2-pad').style.top = `${gameState.player2_position}px`;

		document.getElementById('ball').style.left = `${gameState.ball_position.x}px`;
		document.getElementById('ball').style.top = `${gameState.ball_position.y}px`;

		document.getElementById('player1-score').textContent = gameState.player1_score;
		document.getElementById('player2-score').textContent = gameState.player2_score;

		document.getElementById('game-text').textContent = gameState.game_text;
	}

	////////////////////////////CHAT////////////////////////////////////
	class ChatInput {
		constructor(roomName, username, chatSocket) {
			this.roomName = roomName;
			this.username = username.toLowerCase().trim(); // Normalisation du nom d'utilisateur
			this.chatSocket = chatSocket;
			this.messageInput = document.querySelector(`#chat-input-${roomName} input`);
			this.chatButton = document.querySelector(`#chat-input-${roomName} button`);
	
			console.log(`ChatInput initialized for room: ${roomName}, username: ${this.username}`);
			this.initEventListeners();
		}
	
		initEventListeners() {
			// Envoi de message en appuyant sur "Entrée"
			this.messageInput.addEventListener('keypress', (event) => {
				if (event.key === 'Enter') {
					console.log("Enter key pressed, attempting to send message...");
					this.sendMessage();
				}
			});
	
			// Envoi de message en cliquant sur le bouton d'envoi
			this.chatButton.addEventListener('click', () => {
				console.log("Send button clicked, attempting to send message...");
				this.sendMessage();
			});
		}
	
		sendMessage() {
			const message = this.messageInput.value.trim();
			console.log(`Attempting to send message: ${message}`);
			
			if (message) {
				if (message.startsWith('/b ')) {
					const targetUser = message.slice(3).trim().toLowerCase()
					console.log(`Detected block command for user: ${targetUser}`);
					this.sendBlockCommand(targetUser);
				} else if (message.startsWith('/i ')) {
					const targetUser = message.slice(3).trim().toLowerCase();
					console.log(`Detected invite command for user: ${targetUser}`);
					this.sendInviteCommand(targetUser);
				} else {
					console.log("Sending chat message to WebSocket...");
					this.chatSocket.send(JSON.stringify({
						'type': 'chat_message',
						'message': message,
						'username': this.username,
						'room': this.roomName
					}));
				}
				this.messageInput.value = '';  // Effacer le champ de saisie
				console.log("Message input cleared.");
			} else {
				console.warn('Cannot send an empty message.');
			}
		}
	
		sendBlockCommand(targetUser) {
			console.log(`Sending block command to WebSocket for user: ${targetUser}`);
			this.chatSocket.send(JSON.stringify({
				'type': 'block_user',
				'target_user': targetUser,
				'username': this.username,
				'room': this.roomName
			}));
		}
	
		sendInviteCommand(targetUser) {
			console.log(`Sending invite command to WebSocket for user: ${targetUser}`);
			this.chatSocket.send(JSON.stringify({
				'type': 'invite_user',
				'target_user': targetUser,
				'username': this.username,
				'room': this.roomName
			}));
		}
	}
	
	function startChatWebSocket(token, roomName, username) {
		// Vérification de la validité du username
		if (!username || username.trim() === '') {
			console.error("Username is not defined or empty. WebSocket connection aborted.");
			alert("Username is required to join the chat. Please log in.");
			return;
		}

		username = username.toLowerCase().trim(); // Normalisation du nom d'utilisateur
	
		// Vérification si un WebSocket est déjà ouvert pour la room
		if (roomSockets[roomName] && roomSockets[roomName].readyState === WebSocket.OPEN) {
			console.warn(`WebSocket for room ${roomName} already open.`);
			return;
		}
	
		console.log("Initializing chat WebSocket...");
		console.log(`Initializing chat WebSocket for room: ${roomName} with username: ${username}`);
	
		try {
			console.log(`startChatWebSocket: ${roomName} with username: ${username} and token: ${token}`);
			const chatSocket = new WebSocket(`ws://${window.location.host}/ws/chat/${roomName}/`);
	
			// Événement déclenché lorsque la connexion WebSocket est ouverte
			chatSocket.onopen = function () {
				console.log(`Chat WebSocket connection established in room: ${roomName}`);
	
				// Envoi d'un message d'authentification avec le token et le username
				chatSocket.send(JSON.stringify({
					'type': 'authenticate',
					'token': token,
					'room': roomName,
					'username': username
				}));
				console.log(`Authentication message sent for room: ${roomName} with username: ${username}`);
			};
	
			// Gestion des messages reçus du serveur WebSocket
			chatSocket.onmessage = function (event) {
				const data = JSON.parse(event.data);
				console.log(`Message received from server in room ${roomName}:`, data);
			
				switch (data.type) {
					case 'authenticated':
						console.log(`User authenticated successfully in room: ${roomName}`);
						break;
					case 'chat_message':
						const message = data.message;
						const chatLog = document.getElementById(`chat-log-${roomName}`);
						const receivedUsername = data.username || 'Anonymous'; // Utiliser un fallback si le username est manquant
						
						if (chatLog) {
							const messageElement = document.createElement('div');
							messageElement.textContent = `${receivedUsername}: ${message}`;
							chatLog.appendChild(messageElement);
							console.log(`Message displayed in chat log for room: ${roomName}`);
						} else {
							console.error('Chat log element not found');
						}
						break;
					case 'success':  // Nouveau cas pour traiter les messages de succès
						console.log(`Success message received: ${data.message}`);
						alert(`Success: ${data.message}`);  // Vous pouvez remplacer l'alerte par une notification visuelle plus adaptée
						break;
					case 'error':
						console.error(`Error message received: ${data.message}`);
						alert(`Error: ${data.message}`);  // Afficher une alerte ou un message d'erreur à l'utilisateur
						break;
					default:
						console.warn('Unhandled message type:', data);
				}
			};
	
			// Gestion de la fermeture du WebSocket
			chatSocket.onclose = function (event) {
				if (event.wasClean) {
					console.log(`Chat WebSocket closed cleanly for room ${roomName}, code=${event.code}, reason=${event.reason}`);
				} else {
					console.error(`Chat WebSocket closed unexpectedly for room ${roomName}`);
				}
			};
	
			// Gestion des erreurs WebSocket
			chatSocket.onerror = function (error) {
				console.error(`Chat WebSocket error in room ${roomName}:`, error);
			};
	
			// Stocker la connexion WebSocket dans roomSockets
			roomSockets[roomName] = chatSocket;
			console.log(`WebSocket connection stored for room: ${roomName}`);
	
			// Initialiser l'interface de chat pour cette room
			new ChatInput(roomName, username, chatSocket);
	
		} catch (error) {
			console.error(`Error initializing chat WebSocket for room ${roomName}:`, error);
		}
	}
	
	function createRoomTab(token, roomName, username) {
		console.log(`createRoomTab: ${roomName} with username: ${username} and token: ${token}`);

		const tabContainer = document.getElementById('room-tabs-container');
		if (!tabContainer) {
			console.error('Room tabs container not found.');
			return;
		}

		const existingTab = Array.from(tabContainer.children).find(tab => tab.dataset.room === roomName);
		if (existingTab) {
			console.log(`Tab for room ${roomName} already exists.`);
			// Vous pouvez ajouter une classe pour indiquer que l'onglet est inactif
			existingTab.classList.remove('active');
		} else {
			console.warn(`Tab for room ${roomName} not found in the HTML.`);
		}
	}

	function showRoomTab(roomName) {
		const tabContainer = document.getElementById('room-tabs-container');
		const tab = Array.from(tabContainer.children).find(tab => tab.dataset.room === roomName);
		if (tab) {
			// Vous pouvez ajouter une classe pour indiquer que l'onglet est actif
			tab.classList.add('active');
			console.log(`Showing tab for room: ${roomName}`);
		} else {
			console.warn(`Tab for room ${roomName} not found.`);
		}
	}

	function switchRoom(token, roomName, username) {
		console.log(`switchRoom: ${roomName} with username: ${username} and token: ${token}`);

		if (!roomName) {
			console.error('Room name is undefined.');
			return;
		}
		console.log(`Attempting to switch to room: ${roomName}`);
		if (activeRoom === roomName) {
			console.log(`Already in room: ${roomName}`);
			return;
		}

		console.log(`Switching from room ${activeRoom} to room ${roomName}`);
		const previousRoom = activeRoom;
		activeRoom = roomName;

		if (previousRoom && document.getElementById(`chat-log-${previousRoom}`)) {
			console.log(`Hiding chat log for previous room: ${previousRoom}`);
			document.getElementById(`chat-log-${previousRoom}`).style.display = 'none';
		}

		const chatLog = document.getElementById(`chat-log-${roomName}`);
		if (chatLog) {
			chatLog.style.display = 'block';
		} else {
			console.warn(`No chat log found for room: ${roomName}`);
		}

		// Mettre à jour l'affichage des inputs
		document.querySelectorAll('.chat-input').forEach(input => {
			input.style.display = 'none';
		});
		document.getElementById(`chat-input-${roomName}`).style.display = 'block';

		// Mettre à jour l'onglet actif
		const tabs = document.querySelectorAll('.room-tab');
		tabs.forEach(t => t.classList.remove('active'));
		const activeTab = Array.from(tabs).find(tab => tab.dataset.room === roomName);
		if (activeTab) {
			activeTab.classList.add('active');
		}
	}

	function joinRoom(token, roomName, username) {
		// Vérifier si la room est déjà active
		console.log(`Joining room: ${roomName} with username: ${username} and token: ${token}`);
		if (activeRoom === roomName) {
			console.log(`Already in room: ${roomName}`);
			return;
		}

		if (!roomSockets[roomName]) {
			console.log(`Joining new room: ${roomName}`);
			createRoomTab(token, roomName, username);
			showRoomTab(roomName);
			startChatWebSocket(token, roomName, username);
		}

		switchRoom(token, roomName, username);
	}
});
