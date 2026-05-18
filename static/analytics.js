(function () {

    // =========================
    // CONFIG
    // =========================
    const ENDPOINTS = {
        click: "/userprofile/track_click/",
        search: "/userprofile/track_search/",
        funnel: "/userprofile/track_funnel/"
    };

    let lastClickTime = 0;

    // =========================
    // SAFE FETCH WRAPPER
    // =========================
    function send(url, data) {

        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },

            // 🔥 IMPORTANT: better for production than same-origin
            credentials: "include",

            body: JSON.stringify(data)
        })
        .then(async res => {
            if (!res.ok) {
                const text = await res.text();
                console.warn("Analytics error:", text);
            }
        })
        .catch(err => {
            console.log("Analytics failed:", err);
        });
    }

    // =========================
    // CLICK TRACKING (FIXED)
    // =========================
    document.addEventListener("click", function (e) {

        const now = Date.now();
        if (now - lastClickTime < 250) return;
        lastClickTime = now;

        const target = e.target;
        if (!target) return;

        if (target.tagName === "HTML" || target.tagName === "BODY") return;

        const label =
            target.getAttribute("data-track") ||
            target.dataset.label ||
            target.innerText ||
            target.id ||
            target.className ||
            target.tagName;

        send(ENDPOINTS.click, {
            page: window.location.pathname,
            event_type: "click",
            label: String(label).substring(0, 200),
            x: e.clientX,
            y: e.clientY,
            screen_width: window.innerWidth,
            screen_height: window.innerHeight
        });

    }, true);

    // =========================
    // SEARCH TRACKING
    // =========================
    document.addEventListener("submit", function (e) {

        const form = e.target;
        if (!form) return;

        const input = form.querySelector('input[type="search"]');
        if (!input) return;

        const query = input.value.trim();
        if (!query) return;

        send(ENDPOINTS.search, {
            query: query,
            page: window.location.pathname
        });

    });

    // =========================
    // BUTTON-ONLY TRACKING
    // =========================
    document.addEventListener("click", function (e) {

        const el = e.target;
        if (!el) return;

        if (el.dataset && el.dataset.trackEvent === "true") {

            send(ENDPOINTS.click, {
                page: window.location.pathname,
                event_type: "button_click",
                label: el.dataset.label || el.innerText || "button",
                x: e.clientX,
                y: e.clientY
            });
        }

    });

    // =========================
    // FUNNEL TRACKING (FIXED)
    // =========================
    function trackFunnel(data) {

        send(ENDPOINTS.funnel, {
            funnel_name: data.funnel_name,
            step_number: data.step_number,
            step_name: data.step_name,
            metadata: data.metadata || {}
        });
    }

    // expose globally
    window.trackFunnel = trackFunnel;

})();