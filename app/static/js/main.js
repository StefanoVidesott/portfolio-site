/* ================= MENU RESPONSIVE ================= */
document.addEventListener("DOMContentLoaded", () => {
    const navToggle = document.querySelector(".nav-toggle");
    const navMenu = document.querySelector(".nav-menu");

    if (navToggle && navMenu) {
        navToggle.addEventListener("click", () => {
            navMenu.classList.toggle("nav-menu_visible");

            if (navMenu.classList.contains("nav-menu_visible")) {
                navToggle.setAttribute("aria-label", "Chiudi menu");
            } else {
                navToggle.setAttribute("aria-label", "Apri menu");
            }
        });
    }

    // /* ================= SMOOTH SCROLL ================= */
    // const links = document.querySelectorAll('a[href^="#"]');
    // links.forEach(link => {
    //     link.addEventListener("click", function(e) {
    //         const target = document.querySelector(this.getAttribute("href"));
    //         if (target) {
    //             e.preventDefault();
    //             target.scrollIntoView({ behavior: "smooth" });
    //         }
    //     });
    // });
});
