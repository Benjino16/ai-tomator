export function makeOverlayClosable(overlay) {
    const content = overlay.querySelector(".overlay-content");

    overlay.addEventListener("click", () => {
        overlay.classList.add("hidden");
    });

    content.addEventListener("click", (e) => {
        e.stopPropagation();
    });
}