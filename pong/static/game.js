document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired'); 
    const checkNicknameButton = document.getElementById('check-nickname');
    const registerButton = document.getElementById('register');
    const loginButton = document.getElementById('login');
    const authForm = document.getElementById('auth-form');
    const gameContainer = document.getElementById('game1');
    const nicknameInput = document.getElementById('nickname');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const loginPasswordInput = document.getElementById('login-password');
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const formBlock = document.getElementById('block-form');
    //const viewSelector = document.getElementById('view-selector');
    //const viewPlayersButton = document.getElementById('view-players');
    //const viewMatchesButton = document.getElementById('view-matches');
    const menuButton = document.querySelector('.burger-menu');
    const playerList = document.getElementById('player-list');
    const matchList = document.getElementById('match-list');
    const dropdownMenu = document.getElementById('dropdown-menu');


    let socket;
    let token;
    let gameState;

    // Auto-focus and key handling for AUTH-FORM
    nicknameInput.focus();
    nicknameInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            checkNicknameButton.click();
        }
    });

    checkNicknameButton.addEventListener('click', handleCheckNickname);
    registerButton.addEventListener('click', handleRegister);
    loginButton.addEventListener('click', handleLogin);


    async function handleCheckNickname() {
        const nickname = nicknameInput.value.trim();
        if (nickname) {
            try {
                const exists = await checkUserExists(nickname);
                if (exists) {
                    authForm.style.display = 'none';
                    loginForm.style.display = 'block';
                    // Auto-focus and key handling for LOGIN-FORM
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
                    // Auto-focus and key handling for REGISTER-FORM
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

    async function checkUserExists(username) {
        const response = await fetch('/check_user_exists/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username })
        });
        const data = await response.json();
        return data.exists;
    }

    async function handleRegister() {
        const nickname = nicknameInput.value.trim();
        const password = passwordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();

        if (password === confirmPassword) {
            try {
                const result = await registerUser(nickname, password);
                if (result) {
                    //await createPlayer(nickname);
                    registerForm.style.display = 'none';
                    gameContainer.style.display = 'flex';
                    formBlock.style.display = 'none';
                    startWebSocketConnection(token);
                } else {
                    alert('Registration failed. Please try again.');
                }
            } catch (error) {
                console.error('Error registering user:', error);
            }
        } else {
            alert('Passwords do not match.');
        }
    }

    async function registerUser(username, password) {
        const response = await fetch('/register_user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (data.registered) {
            token = data.token;
        }
        return data.registered;
    }

    async function handleLogin() {
        const nickname = nicknameInput.value.trim();
        const password = loginPasswordInput.value.trim();
        try {
            const result = await authenticateUser(nickname, password);
            if (result) {
                loginForm.style.display = 'none';
                gameContainer.style.display = 'flex';
                formBlock.style.display = 'none';
                startWebSocketConnection(token);
            } else {
                alert('Authentication failed. Please try again.');
            }
        } catch (error) {
            console.error('Error authenticating user:', error);
        }
    }

    async function authenticateUser(username, password) {
        const response = await fetch('/authenticate_user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (data.authenticated) {
            token = data.token;
        }
        return data.authenticated;
    }

    function startWebSocketConnection(token) {
        socket = new WebSocket(`ws://${window.location.host}/ws/game/`);

        socket.onopen = function (event) {
            console.log('WebSocket connection established');
            socket.send(JSON.stringify({ type: 'authenticate', token: token }));
        };

        socket.onmessage = function (event) {
            const data = JSON.parse(event.data);
            if (data.type === 'authenticated') {
                console.log('Authentication successful');
            } else if (data.type === 'waiting_room') {
                console.log('Entered the WAITING ROOM');
            } else if (data.type === 'game_start') {
                console.log('Game started:', data.game_id, '(', data.player1, 'vs', data.player2, ')');
                startGame(data.game_id, data.player1, data.player2);
            } else if (data.type === 'game_state_update') {
                updateGameState(data.game_state);
            } else if (data.type === 'player_disconnected') {
                console.log("Player disconnected:", data.player);
            } else if (data.type === 'game_ended') {
                console.log("Game ended:", data.game_id);
            } else if (data.type === 'error') {
                console.error(data.message);
            } else {
                console.log('Message from server:', data.type, data.message);
            }
        };

        socket.onclose = function (event) {
            console.log('WebSocket connection closed');
        };

        socket.onerror = function (error) {
            console.error('WebSocket error:', error);
        };
    }

    function startGame(gameCode, player1_name, player2_name) {
        document.getElementById('gameCode').textContent = `Game Code: ${gameCode}`;
        document.getElementById('player1-name').textContent = `${player1_name}`;
        document.getElementById('player2-name').textContent = `${player2_name}`;
        document.addEventListener('keydown', handleKeyDown);

    }

    function handleKeyDown(event) {
        if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
            console.log('Key press: ', event.key);
            sendKeyPress(event.key.toLowerCase());
        }
    }

    function sendKeyPress(key) {
        if (socket.readyState === WebSocket.OPEN) {
            console.log('Key sent: ', key);
            socket.send(JSON.stringify({ type: 'key_press', key }));
        }
    }

    function updateGameState(newState) {
        gameState = newState;
        renderGame();
    }

    function renderGame() {
        const player1Pad = document.getElementById('player1-pad');
        player1Pad.style.top = `${gameState.player1_position}px`;

        const player2Pad = document.getElementById('player2-pad');
        player2Pad.style.top = `${gameState.player2_position}px`;

        const ball = document.getElementById('ball');
        ball.style.left = `${gameState.ball_position.x}px`;
        ball.style.top = `${gameState.ball_position.y}px`;

        const player1Score = document.getElementById('player1-score');
        player1Score.textContent = gameState.player1_score;

        const player2Score = document.getElementById('player2-score');
        player2Score.textContent = gameState.player2_score;
    }

    // viewSelector.addEventListener('change', function() {
      //  const selectedView = this.value;
        
        // Masquer les deux listes par défaut
       // playerList.style.display = 'none';
       // matchList.style.display = 'none';

        // Afficher la liste sélectionnée
       // if (selectedView === 'player-list') {
       //     playerList.style.display = 'block';
       //     fetchPlayers();
        //} else if (selectedView === 'match-list') {
        //    matchList.style.display = 'block';
        //    fetchMatches();
        //}
    //}) 

    console.log('Here');

    function toggleMenu() {
        console.log('Menu toggled');
        if (dropdownMenu.style.display === "block") {
            dropdownMenu.style.display = "none";
        } else {
            dropdownMenu.style.display = "block";
        }
    }

    function showTable(tableId) {
        // Masquer tous les tableaux
        if (playerList) {
            playerList.style.display = 'none';
        }
        if (matchList) {
            matchList.style.display = 'none';
        }

        // Afficher le tableau sélectionné
        if (tableId === 'player-list') {
            if (playerList) {
                playerList.style.display = 'block';
            }
            fetchPlayers();
        } else if (tableId === 'match-list') {
            if (matchList) {
                matchList.style.display = 'block';
            }
            fetchMatches();
        }

        // Masquer le menu après la sélection
        if (dropdownMenu) {
            dropdownMenu.style.display = 'none';
        }
    }

    // Ajouter les gestionnaires d'événements
    if (menuButton) {
        menuButton.addEventListener('click', toggleMenu);
    }

    const links = document.querySelectorAll('#dropdown-menu a');
    links.forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault(); // Empêche le comportement par défaut du lien
            const tableId = link.getAttribute('data-table');
            showTable(tableId);
        });
    });

    function fetchMatches() {
        fetch('/api/match_list/')
            .then(response => response.json())
            .then(data => {
                if (data.matches) {
                    displayMatches(data.matches);
                }
            })
            .catch(error => console.error('Error fetching match data:', error));
    }

    function fetchPlayers(){
        fetch('/api/player_list/')
            .then(response => response.json())
            .then(data => {
                if (data.players) {
                    displayPlayers(data.players);
                }
            })
            .catch(error => console.error('Error fetching match data:', error));
    }

    function displayMatches(matches) {
        const matchListBody = document.querySelector('#match-list tbody');
        matchListBody.innerHTML = '';

        matches.forEach(match => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${match.id}</td>
                <td>${match.player1__name}</td>
                <td>${match.player2__name}</td>
                <td>${match.score_player1}</td>
                <td>${match.score_player2}</td>
                <td>${match.winner__name}</td>
                <td>${match.nbr_ball_touch_p1}</td>
                <td>${match.nbr_ball_touch_p2}</td>
                <td>${match.duration}</td>
                <td>${match.date}</td>
                <td>${match.is_tournoi}</td>
                <td>${match.tournoi__name}</td>
            `;
            matchListBody.appendChild(row);
        });
    }

    function displayPlayers(players) {
        const playersListBody = document.querySelector('#player-list tbody');
        playersListBody.innerHTML = '';

        players.forEach(player => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${player.id}</td>
                <td>${player.name}</td>
                <td>${player.total_match}</td>
                <td>${player.total_win}</td>
                <td>${player.p_win}</td>
                <td>${player.m_score_match}</td>
                <td>${player.m_score_adv_match}</td>
                <td>${player.best_score}</td>
                <td>${player.m_nbr_ball_touch}</td>
                <td>${player.total_duration}</td>
                <td>${player.m_duration}</td>
                <td>${player.num_participated_tournaments}</td>
                <td>${player.num_won_tournaments}</td>
            `;
            playersListBody.appendChild(row);
        });
    }

});
