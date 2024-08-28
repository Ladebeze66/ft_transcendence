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

    const menuButton = document.querySelector('.burger-menu');
    const dropdownMenu = document.getElementById('dropdown-menu');

    const playerList = document.getElementById('player-list');
    const matchList = document.getElementById('match-list');
    const tournoiList = document.getElementById('tournoi-list');
    const blockchainList = document.getElementById('blockchain-list');

    const pongElements = document.getElementById('pong-elements');
    const logo = document.querySelector('.logo');

    const localGameButton = document.getElementById('local-game');
    const quickMatchButton = document.getElementById('quick-match');
    const tournamentButton = document.getElementById('tournament');

 /*    const modal = document.getElementById("myModal");
    const btn = document.getElementById("myBtn");
    const span = document.getElementsByClassName("close")[0];
    const jsonContent = document.getElementById("jsonContent"); */

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

    // functions to handle the second player

    async function handleCheckNickname2() {
        const nickname2 = nicknameInput2.value.trim();
        if (nickname2) {
            try {
                const exists = await checkUserExists2(nickname2);
                if (exists) {
                    authForm2.style.display = 'none';
                    loginForm2.style.display = 'block';
                    // Auto-focus and key handling for LOGIN-FORM2
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
                    // Auto-focus and key handling for REGISTER-FORM2
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
        //menuButton.style.display = 'none';
        formBlock.style.display = 'none';
        startWebSocketConnection(token, 2);
    }

    function startQuickMatch() {
        gameContainer.style.display = 'flex';
        logo.style.display = 'none';
        pongElements.style.display = 'none';
        //menuButton.style.display = 'none';
        formBlock.style.display = 'none';
        startWebSocketConnection(token, 1);
    }

    function startTournament() {
        console.log("For now, do nothing, hurry up and work Senor chaku !!!!")
    }

    function startWebSocketConnection(token, players) {
        socket = new WebSocket(`ws://${window.location.host}/ws/game/`);

        socket.onopen = function (event) {
            console.log('WebSocket connection established');
            if (players === 1) {
                console.log("Sending token for 1 player game");
                socket.send(JSON.stringify({ type: 'authenticate', token: token }));
            } else {
                console.log("Sending tokens for 2 player game");
                socket.send(JSON.stringify({ type: 'authenticate2', token_1: token, token_2: token2 }));
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
        if (event.key === 'ArrowUp' || event.key === 'ArrowDown' || event.key === 'w' || event.key === 's') {
            //console.log('Key press: ', event.key);
            sendKeyPress(event.key.toLowerCase());
        }
    }

    function sendKeyPress(key) {
        if (socket.readyState === WebSocket.OPEN) {
            //console.log('Key sent: ', key);
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


    ////////////////////////////// BEG BURGER BUTTON ////////////////////////////////

    menuButton.addEventListener('click', toggleMenu);

    function toggleMenu() {
        console.log('Menu toggled');
        if (dropdownMenu.style.display === "block") {
            dropdownMenu.style.display = "none";
            hideAllTables();
        } else {
            dropdownMenu.style.display = "block";
        }
    }

    function hideAllTables(){
        if (playerList) playerList.style.display = 'none';
        if (matchList) matchList.style.display = 'none';
        if (tournoiList) tournoiList.style.display = 'none';
        if (blockchainList) blockchainList.style.display = 'none';
    }

    const links = document.querySelectorAll('#dropdown-menu a');

    links.forEach(link => {
        link.addEventListener('click', (event) => {
            event.preventDefault(); // Empêche le comportement par défaut du lien
            const tableId = link.getAttribute('data-table');
            //console.log("Here !!!!!!!!!!!! NNNNNNNN");
            showTable(tableId);
        });
    });
    
    function showTable(tableId) {
        // Masquer tous les tableaux
        console.log('Entering showTable', tableId);
        hideAllTables();
    
        // Afficher le tableau sélectionné
        if (tableId === 'player-list') {
            console.log('Showing player list 2');
            //if (playerList) {
            playerList.style.display = 'block';
            fetchPlayers();
            //}
        } else if (tableId === 'match-list') {
            console.log('Showing match list 2');
            //if (matchList) 
            matchList.style.display = 'block';
            fetchMatches();
        } else if (tableId === 'tournoi-list') {
            console.log('Showing tournoi list 2');
            //if (tournoiList) 
            tournoiList.style.display = 'block';
            fetchTournois();
        } else if (tableId === 'blockchain-list') {
            console.log('Opening external page in a new tab');
            window.open('https://sepolia.etherscan.io/address/0x078d04eb6fb97cd863361fc86000647dc876441b', '_blank');
            /* fetch('/web3/')
                .then(response => response.json())
                .then(data => {
                    console.log('ok here !!');
                    jsonContent.textContent = JSON.stringify(data, null, 2);
                }); */
        }
        
        // Masquer le menu après la sélection
        if (dropdownMenu) {
            dropdownMenu.style.display = 'none';
        }
    }

    function fetchMatches() {
        console.log('Fetching matches...');
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
        console.log('Fetching players...');
        fetch('/api/player_list/')
            .then(response => response.json())
            .then(data => {
                if (data.players) {
                    displayPlayers(data.players);
                }
            })
            .catch(error => console.error('Error fetching match data:', error));
    }

    function fetchTournois(){
        console.log('Fetching tournois...');
        fetch('/api/tournoi_list/')
            .then(response => response.json())
            .then(data => {
                if (data.tournois) {
                    displayTournois(data.tournois);
                }
            })
            .catch(error => console.error('Error fetching match data:', error));
    }

    function displayMatches(matches) {
        console.log('Displaying matches:');
        const matchListBody = document.querySelector('#match-list tbody');
        matchListBody.innerHTML = '';

        if (matches.length === 0) {
            console.log('No matches to display');
        }

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
        console.log('Displaying players:');
        const playersListBody = document.querySelector('#player-list tbody');
        playersListBody.innerHTML = '';

        if (players.length === 0) {
            console.log('No players to display');
        }

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

    function displayTournois(tournois) {
        console.log('Displaying tournois:');
        const tournoisListBody = document.querySelector('#tournoi-list tbody');
        tournoisListBody.innerHTML = '';

        if (tournois.length === 0) {
            console.log('No tournois to display');
        }

        tournois.forEach(tournoi => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${tournoi.id}</td>
                <td>${tournoi.name}</td>
                <td>${tournoi.nbr_player}</td>
                <td>${tournoi.date}</td>
                <td>${tournoi.winner.name}</td>
            `;
            tournoisListBody.appendChild(row);
        });
    }

    ////////////////////////////// END BURGER BUTTON ////////////////////////////////


    //////////////////////////////    BEG STARS      ////////////////////////////////

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

    //////////////////////////////    END STARS      ////////////////////////////////

    
   /*  btn.onclick = function() {
        fetch('/web3/')
            .then(response => response.json())
            .then(data => {
                console.log('ok here !!');
                jsonContent.textContent = JSON.stringify(data, null, 2);
                modal.style.display = "block";
            });
    }

    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    } */

    //////////////////////////////    BEG LANGAGE    ////////////////////////////////
    const translations = {
        fr: {
            welcome: "BIENVENUE DANS LE PONG 42",
            labelNickname: "Entrez votre surnom:",
            labelPassword: "Entrez votre mot de passe:",
            labelConfirmPassword: "Confirmez votre mot de passe:",
            labelLoginPassword: "Entrez votre mot de passe:"
        },
        en: {
            welcome: "WELCOME TO PONG 42",
            labelNickname: "Enter your nickname:",
            labelPassword: "Enter your password:",
            labelConfirmPassword: "Confirm your password:",
            labelLoginPassword: "Enter your password:"
        },
        it: {
            welcome: "BENVENUTO A PONG 42",
            labelNickname: "Inserisci il tuo soprannome:",
            labelPassword: "Inserisci la tua password:",
            labelConfirmPassword: "Conferma la tua password:",
            labelLoginPassword: "Inserisci la tua password:"
        },
        es: {
            welcome: "BIENVENIDO A PONG 42",
            labelNickname: "Introduce tu apodo:",
            labelPassword: "Introduce tu contraseña:",
            labelConfirmPassword: "Confirma tu contraseña:",
            labelLoginPassword: "Introduce tu contraseña:"
        },
        de: {
            welcome: "WILLKOMMEN BEI PONG 42",
            labelNickname: "Geben Sie Ihren Spitznamen ein:",
            labelPassword: "Geben Sie Ihr Passwort ein:",
            labelConfirmPassword: "Bestätigen Sie Ihr Passwort:",
            labelLoginPassword: "Geben Sie Ihr Passwort ein:"
        }
    };

    function setCookie(name, value, days) {
        const d = new Date();
        d.setTime(d.getTime() + (days*24*60*60*1000));
        const expires = "expires=" + d.toUTCString();
        document.cookie = name + "=" + value + ";" + expires + ";path=/";
    }

    function getCookie(name) {
        const cname = name + "=";
        const decodedCookie = decodeURIComponent(document.cookie);
        const ca = decodedCookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(cname) === 0) {
                return c.substring(cname.length, c.length);
            }
        }
        return "";
    }

    function changeLanguage(lang) {
        setCookie('preferredLanguage', lang, 365);  // Store the language preference for 1 year
        document.getElementById('welcome').innerText = translations[lang].welcome;
        document.getElementById('label-nickname').innerText = translations[lang].labelNickname;
        document.getElementById('label-password').innerText = translations[lang].labelPassword;
        document.getElementById('label-confirm-password').innerText = translations[lang].labelConfirmPassword;
        document.getElementById('label-login-password').innerText = translations[lang].labelLoginPassword;
    }

    // Function to set the language based on the cookie
    function setLanguageFromCookie() {
        const preferredLanguage = getCookie('preferredLanguage');
        if (preferredLanguage && translations[preferredLanguage]) {
            changeLanguage(preferredLanguage);
        } else {
            changeLanguage('fr'); // Default to French if no cookie is found
        }
    }

    document.getElementById('lang-fr').addEventListener('click', () => changeLanguage('fr'));
    document.getElementById('lang-en').addEventListener('click', () => changeLanguage('en'));
    document.getElementById('lang-it').addEventListener('click', () => changeLanguage('it'));
    document.getElementById('lang-es').addEventListener('click', () => changeLanguage('es'));
    document.getElementById('lang-de').addEventListener('click', () => changeLanguage('de'));

    // Set the language when the page loads
    window.onload = setLanguageFromCookie;

    //////////////////////////////   END LANGAGE    ////////////////////////////////



    //////////////////////////////    BEG SETTING     ////////////////////////////////
    
    document.getElementById('settings-btn').addEventListener('click', function() {
        document.getElementById('settings-menu').style.display = 'block';
    });

    document.getElementById('close-settings').addEventListener('click', function() {
        document.getElementById('settings-menu').style.display = 'none';
    });

    // Change the color of the text
    document.getElementById('color-picker').addEventListener('input', function() {
        document.body.style.color = this.value;
        document.querySelectorAll('button').forEach(function(button) {
            button.style.backgroundColor = this.value;  // Change la couleur de fond des boutons
        }, this);
    });

    document.getElementById('font-selector').addEventListener('change', function() {
        document.body.style.fontFamily = this.value;
    });

    document.getElementById('font-size-slider').addEventListener('input', function() {
        document.body.style.fontSize = this.value + 'px';
    });

    //////////////////////////////    END SETTING     ////////////////////////////////

});
