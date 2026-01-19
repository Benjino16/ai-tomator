import { FilesUI } from "./ui/files_ui.js";
import { EndpointsUI } from "./ui/endpoints_ui.js";
import { RunsUI } from "./ui/batches_ui.js";
import { ExportUI } from "./ui/export_ui.js";
import {PromptsUI as PromptUI} from "./ui/prompts_ui.js";
import { API } from "./api/index.js";

function init() {
    console.log("INIT");
    FilesUI.init();
    EndpointsUI.init();
    RunsUI.init();
    ExportUI.init();
    PromptUI.init();
}



function checkAuthentication() {
    API.Login.authme().then(authme => {
        if (authme.success) {
            loginSuccess()
        }
        else {
            document.querySelector('.layout').style.display = 'none';
        }
    })
}


const authOverlay = document.getElementById('authOverlay');
const authForm = document.getElementById('authForm');
const loginBtn = document.getElementById('loginBtn');
const registerBtn = document.getElementById('registerBtn');
const logoutBtn = document.getElementById('logoutBtn');

// Login
authForm.addEventListener('submit', function(e){
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    API.Login.login(username, password).then(result => {
        if(result.success) {
            checkAuthentication()
            document.getElementById('username').value = "";
            document.getElementById('password').value = "";
        }
        else {
            alert(result.detail);
        }
    })
});

// Register
registerBtn.addEventListener('click', function(){
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    API.Login.register(username, password).then(result => {
        if(result.success) {
            alert("Benutzer registriert! Du kannst dich jetzt einloggen.");
        }
        else {
            alert(result.detail);
        }
    })
});

logoutBtn.addEventListener('click', async () => {
    try {
        API.Login.logout().then(result => {
            if(result.success){
                document.querySelector('.layout').style.display = 'none';
                authOverlay.style.display = 'flex';
            } else {
                alert("Logout failed!");
            }
        });
    } catch(err){
        console.error("Logout error:", err);
    }
});

function loginSuccess(){
    // Overlay verstecken
    authOverlay.style.display = 'none';
    // Dashboard anzeigen
    document.querySelector('.layout').style.display = 'flex';

    const warningOverlay = document.getElementById("warning-overlay");
    const understandWarningBtn = document.getElementById("understand-warning-btn");

    const understoodWarning = sessionStorage.getItem("understoodWarning");
    if (!understoodWarning) {
        warningOverlay.classList.remove("hidden");
    }

    understandWarningBtn.addEventListener("click", function() {
        warningOverlay.classList.add("hidden");
        sessionStorage.setItem("understoodWarning", "true");
    })

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
}

checkAuthentication();