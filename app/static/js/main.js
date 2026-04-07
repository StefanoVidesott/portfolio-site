document.addEventListener("DOMContentLoaded", () => {

    // -----------------------------------------------------------------------
    // Mobile navigation toggle
    // -----------------------------------------------------------------------
    const navToggle = document.querySelector(".nav-toggle");
    const navMenu = document.querySelector(".nav-menu");

    if (navToggle && navMenu) {
        const labelOpen = navToggle.dataset.labelOpen;
        const labelClose = navToggle.dataset.labelClose;

        navToggle.addEventListener("click", () => {
            const isOpen = navMenu.classList.toggle("nav-menu_visible");
            navToggle.setAttribute("aria-label", isOpen ? labelClose : labelOpen);
            navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        });
    }

    // -----------------------------------------------------------------------
    // Scroll-reveal animations
    // -----------------------------------------------------------------------
    const revealElements = document.querySelectorAll(".reveal");

    const revealOnScroll = new IntersectionObserver(
        (entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("active");
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.15, rootMargin: "0px 0px -50px 0px" }
    );

    revealElements.forEach(el => revealOnScroll.observe(el));
// -----------------------------------------------------------------------
    // Enhanced Hacker / Decode Animation
    // -----------------------------------------------------------------------
    const scrambleEl = document.querySelector(".typed-text");
    const cursorSpan = document.querySelector(".cursor");

    if (scrambleEl) {
        // Un set di caratteri più "tecnico" (molti simboli, meno lettere standard)
        const CHARS = "01!@#$%^&*<>[]{}—=+_~/?\\|01";
        const DECODE_CHAR_MS = 60;   // Tempo di "blocco" per ogni singola lettera corretta
        const PAUSE_MS       = 2500; // Pausa a parola completata
        const SCRAMBLE_IN_MS = 400;  // Durata della transizione puro "rumore"

        const words = scrambleEl.dataset.words.split("|");
        const rand = () => CHARS[Math.floor(Math.random() * CHARS.length)];

        /** Renderizza la parte bloccata (corretta) e aggiunge il rumore in coda */
        function render(word, lockedCount, currentLength) {
            let out = word.slice(0, lockedCount);
            // Il rumore riempie lo spazio rimanente fino alla currentLength
            const noiseLength = Math.max(0, currentLength - lockedCount);
            for (let i = 0; i < noiseLength; i++) {
                out += rand();
            }
            scrambleEl.textContent = out;
        }

        /** * Transizione di puro rumore: interpola fluidamente la lunghezza
         * dalla parola precedente a quella successiva.
         */
        function scrambleIn(oldLength, newLength, duration) {
            return new Promise(resolve => {
                const startTime = performance.now();

                (function frame(now) {
                    const elapsed = now - startTime;
                    const progress = Math.min(elapsed / duration, 1);

                    // Calcola la lunghezza attuale basandosi sul progresso
                    const currentLength = Math.round(oldLength + (newLength - oldLength) * progress);

                    let out = "";
                    for (let i = 0; i < currentLength; i++) out += rand();
                    scrambleEl.textContent = out;

                    if (progress < 1) {
                        requestAnimationFrame(frame);
                    } else {
                        resolve();
                    }
                })(performance.now());
            });
        }

        /** Decodifica da sinistra a destra ad ogni frame visivo */
        function decode(word) {
            return new Promise(resolve => {
                let locked = 0;
                const startTime = performance.now();

                (function frame(now) {
                    // Calcola quante lettere dovrebbero essere bloccate in base al tempo trascorso
                    locked = Math.floor((now - startTime) / DECODE_CHAR_MS);

                    if (locked < word.length) {
                        // Passiamo la lunghezza della parola target, così non ci sono sbalzi
                        render(word, locked, word.length);
                        requestAnimationFrame(frame);
                    } else {
                        scrambleEl.textContent = word; // Fissa la parola finale
                        resolve();
                    }
                })(performance.now());
            });
        }

        const wait = ms => new Promise(r => setTimeout(r, ms));

        async function run() {
            let i = 0;
            let currentLength = words[i].length;

            if (cursorSpan) cursorSpan.classList.add("typing");
            await decode(words[i]);

            while (true) {
                if (cursorSpan) cursorSpan.classList.remove("typing");
                await wait(PAUSE_MS);
                if (cursorSpan) cursorSpan.classList.add("typing");

                const nextIndex = (i + 1) % words.length;
                const nextLength = words[nextIndex].length;

                // Scramble puro passando gradualmente dalla lunghezza vecchia a quella nuova
                await scrambleIn(currentLength, nextLength, SCRAMBLE_IN_MS);

                // Decodifica la nuova parola
                await decode(words[nextIndex]);

                currentLength = nextLength;
                i = nextIndex;
            }
        }

        // Avvio opzionale con un piccolo ritardo per permettere al DOM di caricare
        setTimeout(run, 200);
    }

    // -----------------------------------------------------------------------
    // Theme toggle (persisted in localStorage)
    // Note: the initial theme is applied before DOMContentLoaded via an
    // inline script in <head> to prevent flash of unstyled content.
    // -----------------------------------------------------------------------
    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = themeToggle ? themeToggle.querySelector("i") : null;
    const root = document.documentElement;

    if (themeToggle && themeIcon) {
        const currentTheme = root.getAttribute("data-theme") || "dark";

        if (currentTheme === "light") {
            themeIcon.classList.replace("fa-sun", "fa-moon");
        }

        themeToggle.addEventListener("click", () => {
            const isDark = root.getAttribute("data-theme") === "dark";
            const next = isDark ? "light" : "dark";
            root.setAttribute("data-theme", next);
            localStorage.setItem("theme", next);
            themeIcon.classList.replace(isDark ? "fa-sun" : "fa-moon", isDark ? "fa-moon" : "fa-sun");
        });
    }

    // -----------------------------------------------------------------------
    // Contact form — i18n strings come from data-* attributes on the form
    // -----------------------------------------------------------------------
    const contactForm = document.getElementById("contactForm");
    const formResponse = document.getElementById("formResponse");
    const submitBtn = document.getElementById("submitBtn");
    const btnText = document.getElementById("btnText");

    if (contactForm) {
        const msgCaptcha = contactForm.dataset.msgCaptcha;
        const msgSending = contactForm.dataset.msgSending;
        const msgSuccess = contactForm.dataset.msgSuccess;
        const msgError = contactForm.dataset.msgError;

        contactForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const originalText = btnText.innerText;
            submitBtn.disabled = true;
            btnText.innerText = msgSending;
            formResponse.className = "form-message";

            const tokenElement = document.querySelector('[name="cf-turnstile-response"]');
            const turnstileToken = tokenElement ? tokenElement.value : "";

            if (!turnstileToken) {
                formResponse.innerText = msgCaptcha;
                formResponse.classList.add("error");
                submitBtn.disabled = false;
                btnText.innerText = originalText;
                return;
            }

            const formData = {
                name: document.getElementById("name").value,
                email: document.getElementById("email").value,
                message: document.getElementById("message").value,
                turnstile_token: turnstileToken,
            };

            try {
                const response = await fetch("/api/contact", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(formData),
                });

                if (response.ok) {
                    formResponse.innerText = msgSuccess;
                    formResponse.className = "form-message success";
                    contactForm.reset();
                    if (typeof turnstile !== "undefined") turnstile.reset();
                } else {
                    throw new Error("Server error");
                }
            } catch {
                formResponse.innerText = msgError;
                formResponse.classList.add("error");
            } finally {
                submitBtn.disabled = false;
                btnText.innerText = originalText;
            }
        });
    }

    // -----------------------------------------------------------------------
    // Language switcher
    // -----------------------------------------------------------------------
    const languageSwitcher = document.getElementById("languageSwitcher");
    if (languageSwitcher) {
        languageSwitcher.addEventListener("change", function () {
            window.location.href = this.value;
        });
    }
});
