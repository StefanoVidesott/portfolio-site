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

    const revealElements = document.querySelectorAll(".reveal");

    const revealOptions = {
        threshold: 0.15,
        rootMargin: "0px 0px -50px 0px"
    };

    const revealOnScroll = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (!entry.isIntersecting) {
                return;
            } else {
                entry.target.classList.add("active");
                observer.unobserve(entry.target);
            }
        });
    }, revealOptions);

    revealElements.forEach(el => {
        revealOnScroll.observe(el);
    });

    const typedTextSpan = document.querySelector(".typed-text");
    const cursorSpan = document.querySelector(".cursor");

    if (typedTextSpan && cursorSpan) {

        const textArray = typedTextSpan.getAttribute("data-words").split("|");

        const typingDelay = 100;
        const erasingDelay = 50;
        const newTextDelay = 2000;
        let textArrayIndex = 0;
        let charIndex = 0;

        function type() {
            if (charIndex < textArray[textArrayIndex].length) {
                if(!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
                typedTextSpan.textContent += textArray[textArrayIndex].charAt(charIndex);
                charIndex++;
                setTimeout(type, typingDelay);
            }
            else {
                cursorSpan.classList.remove("typing");
                setTimeout(erase, newTextDelay);
            }
        }

        function erase() {
            if (charIndex > 0) {
                if(!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
                typedTextSpan.textContent = textArray[textArrayIndex].substring(0, charIndex - 1);
                charIndex--;
                setTimeout(erase, erasingDelay);
            }
            else {
                cursorSpan.classList.remove("typing");
                textArrayIndex++;
                if (textArrayIndex >= textArray.length) textArrayIndex = 0;
                setTimeout(type, typingDelay + 500);
            }
        }

        setTimeout(type, newTextDelay);
    }


    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = themeToggle ? themeToggle.querySelector("i") : null;
    const body = document.documentElement;

    if (themeToggle && themeIcon) {
        const currentTheme = localStorage.getItem("theme");

        if (currentTheme) {
            body.setAttribute("data-theme", currentTheme);
            if (currentTheme === "light") {
                themeIcon.classList.replace("fa-sun", "fa-moon");
            }
        } else {
            body.setAttribute("data-theme", "dark");
        }

        themeToggle.addEventListener("click", () => {
            let theme = body.getAttribute("data-theme");

            if (theme === "dark") {
                body.setAttribute("data-theme", "light");
                localStorage.setItem("theme", "light");
                themeIcon.classList.replace("fa-sun", "fa-moon");
            } else {
                body.setAttribute("data-theme", "dark");
                localStorage.setItem("theme", "dark");
                themeIcon.classList.replace("fa-moon", "fa-sun");
            }
        });
    }

    const contactForm = document.getElementById('contactForm');
    const formResponse = document.getElementById('formResponse');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');

    if (contactForm) {
        contactForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const originalText = btnText.innerText;
            submitBtn.disabled = true;
            btnText.innerText = "Invio in corso...";
            formResponse.className = 'form-message';

            const tokenElement = document.querySelector('[name="cf-turnstile-response"]');
            const turnstileToken = tokenElement ? tokenElement.value : "";

            if (!turnstileToken) {
                formResponse.innerText = "Per favore, attendi la verifica di sicurezza.";
                formResponse.classList.add('error');
                submitBtn.disabled = false;
                btnText.innerText = originalText;
                return;
            }

            const formData = {
                name: document.getElementById('name').value,
                email: document.getElementById('email').value,
                message: document.getElementById('message').value,
                turnstile_token: turnstileToken
            };

            try {
                const response = await fetch('/api/contact', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    formResponse.innerText = "Messaggio inviato con successo!";
                    formResponse.className = 'form-message success';
                    contactForm.reset();
                    if (typeof turnstile !== 'undefined') turnstile.reset();
                } else {
                    throw new Error('Errore dal server');
                }
            } catch (error) {
                formResponse.innerText = "Si è verificato un errore. Riprova più tardi.";
                formResponse.classList.add('error');
            } finally {
                submitBtn.disabled = false;
                btnText.innerText = originalText;
            }
        });
    }

    const languageSwitcher = document.getElementById('languageSwitcher');
    if (languageSwitcher) {
        languageSwitcher.addEventListener('change', function() {
            window.location.href = this.value;
        });
    }
});
