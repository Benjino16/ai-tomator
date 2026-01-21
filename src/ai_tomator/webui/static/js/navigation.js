export function showSection(sectionId) {
    // Alle Sections verstecken
    const sections = document.querySelectorAll("main > section");
    sections.forEach(sec => sec.style.display = "none");

    // Gewählte Section anzeigen
    const activeSection = document.getElementById(sectionId);
    if (activeSection) activeSection.style.display = "block";
}

export function setupNavigation() {
    const navLinks = document.querySelectorAll("aside nav a[href^='#']");
    navLinks.forEach(link => {
        link.addEventListener("click", (e) => {
            e.preventDefault();
            const targetId = link.getAttribute("href").substring(1);
            showSection(targetId);

            // Optional: aktiven Link hervorheben
            navLinks.forEach(l => l.classList.remove("active"));
            link.classList.add("active");
        });
    });
}