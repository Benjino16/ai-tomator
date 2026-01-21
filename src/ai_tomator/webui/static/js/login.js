// login.js
import { API } from "./api/index.js";

export function setupLogin(onLoginSuccess) {
    const authOverlay = document.getElementById('authOverlay');
    const authForm = document.getElementById('authForm');
    const registerBtn = document.getElementById('registerBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    async function checkAuthentication() {
        const authme = await API.Login.authme();
        if (authme.success) {
            onLoginSuccess();
        } else {
            document.querySelector('.layout').style.display = 'none';
        }
    }

    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const result = await API.Login.login(username, password);
        if (result.success) {
            await checkAuthentication();
            document.getElementById('username').value = "";
            document.getElementById('password').value = "";
        } else {
            alert(result.detail);
        }
    });

    registerBtn.addEventListener('click', async () => {
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const result = await API.Login.register(username, password);
        if (result.success) {
            alert("Benutzer registriert! Du kannst dich jetzt einloggen.");
        } else {
            alert(result.detail);
        }
    });

    logoutBtn.addEventListener('click', async () => {
        try {
            const result = await API.Login.logout();
            if(result.success){
                document.querySelector('.layout').style.display = 'none';
                authOverlay.style.display = 'flex';
            } else {
                alert("Logout failed!");
            }
        } catch(err){
            console.error("Logout error:", err);
        }
    });

    // Initialer Auth-Check
    checkAuthentication();
}
