(function () {

    // =========================
    // CONFIG (match your Django URLs)
    // =========================
    const ENDPOINTS = {
        click: "/userprofile/track_click/",
        search: "/userprofile/track_search/"
    };

    // prevent click spam
    let lastClickTime = 0;

    // =========================
    // SAFE REQUEST FUNCTION
    // =========================
    function send(url, data) {

        fetch(url, {
            method: "POST",
            credentials: "same-origin",   // IMPORTANT for Django session
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },
            body: JSON.stringify(data)
        })
        .then(res => {
            if (!res.ok) {
                return res.text().then(t => {
                    console.warn("Analytics error:", t);
                });
            }
        })
        .catch(err => {
            console.log("Analytics failed:", err);
        });
    }

    // =========================
    // CLICK TRACKING
    // =========================
    document.addEventListener("click", function (e) {

        const now = Date.now();

        // debounce clicks (prevents spam)
        if (now - lastClickTime < 200) return;
        lastClickTime = now;

        const target = e.target;

        if (!target) return;

        // ignore body/html clicks
        if (target.tagName === "HTML" || target.tagName === "BODY") return;

        const label =
            target.getAttribute("data-track") ||
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
    // OPTIONAL: TRACK ONLY MARKED ELEMENTS
    // =========================
    document.addEventListener("click", function (e) {

        const el = e.target;

        if (!el) return;

        // only track elements with data-track-event="true"
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

})();


fetch("/userprofile/track_funnel/", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        funnel_name: "signup_flow",
        step_number: 1,
        step_name: "landing_page"
    })
});