// login.js
import { API } from "./api/index.js";

export function setupLogin(onLoginSuccess) {
    const authOverlay = document.getElementById('authOverlay');
    const authForm = document.getElementById('authForm');
    const logoutBtn = document.getElementById('logoutBtn');

    const passwordConfirm = document.getElementById('passwordConfirm');
    const submitBtn = document.getElementById('submitBtn');
    const switchMode = document.getElementById('switchMode');
    const switchText = document.getElementById('switchText');
    const authTitle = document.getElementById('authTitle');

    let isRegisterMode = false;

    function updateMode() {
        isRegisterMode = !isRegisterMode;

        passwordConfirm.style.display = isRegisterMode ? 'block' : 'none';
        passwordConfirm.required = isRegisterMode;

        submitBtn.textContent = isRegisterMode ? 'Registrieren' : 'Login';
        authTitle.textContent = isRegisterMode
            ? 'Account erstellen'
            : 'Willkommen bei AI-Tomator';

        switchText.textContent = isRegisterMode
            ? 'Schon einen Account?'
            : 'Noch keinen Account?';

        switchMode.textContent = isRegisterMode
            ? 'Login'
            : 'Registrieren';
    }

    switchMode.addEventListener('click', (e) => {
        e.preventDefault();
        updateMode();
    });

    async function checkAuthentication() {
        const authme = await API.Login.authme();
        if (authme.success) {
            onLoginSuccess();
        } else {
            document.querySelector('.layout').style.display = 'none';
            authOverlay.style.display = 'flex';
        }
    }

    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const password2 = passwordConfirm.value;

        if (isRegisterMode) {
            if (password !== password2) {
                alert("Passwörter stimmen nicht überein");
                return;
            }

            const result = await API.Login.register(username, password);
            if (result.success) {
                alert("Registrierung erfolgreich. Bitte einloggen.");
                updateMode(); // zurück zu Login
            } else {
                alert(result.detail);
            }
        } else {
            const result = await API.Login.login(username, password);
            if (result.success) {
                await checkAuthentication();
            } else {
                alert(result.detail);
            }
        }

        authForm.reset();
    });

    logoutBtn.addEventListener('click', async () => {
        const result = await API.Login.logout();
        if (result.success) {
            document.querySelector('.layout').style.display = 'none';
            authOverlay.style.display = 'flex';
        }
    });

    checkAuthentication();
}
