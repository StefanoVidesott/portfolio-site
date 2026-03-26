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
    // Typing animation
    // -----------------------------------------------------------------------
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
                if (!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
                typedTextSpan.textContent += textArray[textArrayIndex].charAt(charIndex);
                charIndex++;
                setTimeout(type, typingDelay);
            } else {
                cursorSpan.classList.remove("typing");
                setTimeout(erase, newTextDelay);
            }
        }

        function erase() {
            if (charIndex > 0) {
                if (!cursorSpan.classList.contains("typing")) cursorSpan.classList.add("typing");
                typedTextSpan.textContent = textArray[textArrayIndex].substring(0, charIndex - 1);
                charIndex--;
                setTimeout(erase, erasingDelay);
            } else {
                cursorSpan.classList.remove("typing");
                textArrayIndex = (textArrayIndex + 1) % textArray.length;
                setTimeout(type, typingDelay + 500);
            }
        }

        setTimeout(type, newTextDelay);
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
