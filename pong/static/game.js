document.addEventListener('DOMContentLoaded', () => {
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

    checkNicknameButton2.addEventListener('click', handleCheckNickname2);
    registerButton2.addEventListener('click', handleRegister2);
    loginButton2.addEventListener('click', handleLogin2);

    localGameButton.addEventListener('click', startLocalGame);
    quickMatchButton.addEventListener('click', startQuickMatch);
    tournamentButton.addEventListener('click', startTournament);


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
                    registerForm.style.display = 'none';
                    document.getElementById("post-form-buttons").style.display = 'block';
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
                document.getElementById("post-form-buttons").style.display = 'block';
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

    async function handleRegister2() {
        const nickname2 = nicknameInput2.value.trim();
        const password2 = passwordInput2.value.trim();
        const confirmPassword2 = confirmPasswordInput2.value.trim();

        if (password2 === confirmPassword2) {
            try {
                const result = await registerUser2(nickname2, password2);
                if (result) {
                    registerForm2.style.display = 'none';
                    startLocalGame2();
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

    async function registerUser2(username, password) {
        const response = await fetch('/register_user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (data.registered) {
            token2 = data.token;
        }
        return data.registered;
    }

    async function handleLogin2() {
        const nickname2 = nicknameInput2.value.trim();
        const password2 = loginPasswordInput2.value.trim();
        try {
            const result = await authenticateUser2(nickname2, password2);
            if (result) {
                loginForm2.style.display = 'none';
                startLocalGame2();
            } else {
                alert('Authentication failed. Please try again.');
            }
        } catch (error) {
            console.error('Error authenticating user:', error);
        }
    }

    async function authenticateUser2(username, password) {
        const response = await fetch('/authenticate_user/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        if (data.authenticated) {
            token2 = data.token;
        }
        return data.authenticated;
    }

    function startLocalGame() {
        console.log("starting a Local Game..");
        document.getElementById("post-form-buttons").style.display = 'none';
        authForm2.style.display = 'block';
        nicknameInput2.focus();
        nicknameInput2.addEventListener('keypress', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                checkNicknameButton2.click();
            }
        });
    }

    function startLocalGame2() {
        gameContainer.style.display = 'flex';
        logo.style.display = 'none';
        pongElements.style.display = 'none';
        formBlock.style.display = 'none';
        startWebSocketConnection(token, 2);
    }

    function startQuickMatch() {
        gameContainer.style.display = 'flex';
        logo.style.display = 'none';
        pongElements.style.display = 'none';
        formBlock.style.display = 'none';
        startWebSocketConnection(token, 1);
    }

    function startTournament() {
        tournamentContainer.style.display = 'flex';
        logo.style.display = 'none';
        pongElements.style.display = 'none';
        formBlock.style.display = 'none';
        startWebSocketConnection(token, 42);
    }

    function startWebSocketConnection(token, players) {
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
                console.log("Sending token for a tournament game")
                socket.send(JSON.stringify({ type: 'authenticate3', token: token }));
            }
        };

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

        socket.onclose = function (event) {
            console.log('WebSocket connection closed');
        };

        socket.onerror = function (error) {
            console.error('WebSocket error:', error);
        };
    }

    function handleKeyDown(event) {
        if (event.key === 'ArrowUp' || event.key === 'ArrowDown' || event.key === 'w' || event.key === 's') {
            sendKeyPress(event.key.toLowerCase());
        }
    }

    function sendKeyPress(key) {
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'key_press', key }));
        }
    }

    function updateGameState(newState) {
        gameState = newState;
        renderGame();
    }

    function renderGame() {
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

    const starsContainer = document.getElementById('stars');
    for (let i = 0; i < 500; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.width = `${Math.random() * 3}px`;
        star.style.height = star.style.width;
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.animationDuration = `${Math.random() * 2 + 1}s`;
        starsContainer.appendChild(star);
    }

});
