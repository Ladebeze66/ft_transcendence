document.addEventListener('DOMContentLoaded', () => {
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
        setCookie('preferredLanguage', lang, 365);
        document.getElementById('welcome').innerText = translations[lang].welcome;
        document.getElementById('label-nickname').innerText = translations[lang].labelNickname;
        document.getElementById('label-password').innerText = translations[lang].labelPassword;
        document.getElementById('label-confirm-password').innerText = translations[lang].labelConfirmPassword;
        document.getElementById('label-login-password').innerText = translations[lang].labelLoginPassword;
    }

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

    window.onload = setLanguageFromCookie;

    document.getElementById('settings-btn').addEventListener('click', function() {
        document.getElementById('settings-menu').style.display = 'block';
    });

    document.getElementById('close-settings').addEventListener('click', function() {
        document.getElementById('settings-menu').style.display = 'none';
    });

    
    document.getElementById('color-picker').addEventListener('input', function() {
        document.body.style.color = this.value;
        document.querySelectorAll('button').forEach(function(button) {
            button.style.backgroundColor = this.value;
        }, this);
    });

    document.getElementById('font-selector').addEventListener('change', function() {
        document.body.style.fontFamily = this.value;
    });

    document.getElementById('font-size-slider').addEventListener('input', function() {
        document.body.style.fontSize = this.value + 'px';
    });

});