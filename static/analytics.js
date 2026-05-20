(function () {

    // =========================
    // ENDPOINTS
    // =========================
    const ENDPOINTS = {
        click: "/userprofile/track_click/",
        search: "/userprofile/track_search/",
        funnel: "/userprofile/track_funnel/"
    };

    let lastClickTime = 0;

    // =========================
    // SAFE FETCH
    // =========================
    function send(url, data) {
        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },
            credentials: "include",
            body: JSON.stringify(data)
        }).catch(err => console.log("Analytics failed:", err));
    }

    // =========================
    // LABEL BUILDER
    // =========================
    function getLabel(el) {
        if (!el) return "Unknown";

        const raw =
            el.getAttribute?.("data-track") ||
            el.dataset?.label ||
            el.getAttribute?.("aria-label") ||
            el.id ||
            el.innerText ||
            el.tagName;

        return String(raw).trim().slice(0, 120);
    }

    // =========================
    // SELECTOR BUILDER
    // =========================
    function getSelector(el) {
        if (!el || el.nodeType !== 1) return "";

        if (el.id) return `#${el.id}`;

        let path = [];

        while (el && el.nodeType === 1 && path.length < 5) {
            let selector = el.tagName.toLowerCase();

            if (el.className && typeof el.className === "string") {
                const cls = el.className.trim().split(/\s+/)[0];
                if (cls) selector += "." + cls;
            }

            path.unshift(selector);
            el = el.parentElement;
        }

        return path.join(" > ");
    }

    // =========================
    // DEVICE INFO
    // =========================
    function getDeviceInfo() {
        const ua = navigator.userAgent || "";

        // Device type
        let device_type = "desktop";

        if (/Mobi|Android|iPhone|iPod/i.test(ua)) {
            device_type = /iPad/i.test(ua) ? "tablet" : "mobile";
        }

        // Browser
        let browser = "unknown";

        if (ua.includes("Chrome") && !ua.includes("Edg")) browser = "chrome";
        else if (ua.includes("Firefox")) browser = "firefox";
        else if (ua.includes("Safari") && !ua.includes("Chrome")) browser = "safari";
        else if (ua.includes("Edg")) browser = "edge";

        // OS
        let os = "unknown";

        if (ua.includes("Windows")) os = "windows";
        else if (ua.includes("Mac OS")) os = "macos";
        else if (ua.includes("Android")) os = "android";
        else if (ua.includes("iPhone") || ua.includes("iPad") || ua.includes("iOS")) os = "ios";
        else if (ua.includes("Linux")) os = "linux";

        return { device_type, browser, os };
    }

    // =========================
    // CLICK TRACKING
    // =========================
    document.addEventListener("click", function (e) {

        const now = Date.now();
        if (now - lastClickTime < 200) return;
        lastClickTime = now;

        const el = e.target;
        if (!el || el.tagName === "HTML" || el.tagName === "BODY") return;

        const isTrackedButton = el.dataset?.trackEvent === "true";
        const device = getDeviceInfo();

        send(ENDPOINTS.click, {
            // Page info
            page: window.location.pathname,
            page_title: document.title,
            url: window.location.href,
            referrer: document.referrer || "",

            // Event
            event_type: isTrackedButton ? "button_click" : "click",
            label: getLabel(el),

            // Element info
            element_type: el.tagName || "",
            element_id: el.id || "",
            css_class: typeof el.className === "string" ? el.className : "",
            selector: getSelector(el),

            // Position
            x: e.clientX,
            y: e.clientY,

            // Screen
            screen_width: window.innerWidth,
            screen_height: window.innerHeight,

            // Device info
            device_type: device.device_type,
            browser: device.browser,
            os: device.os
        });

    }, true);

    // =========================
    // SEARCH TRACKING
    // =========================
    document.addEventListener("submit", function (e) {

        const form = e.target;
        if (!form) return;

        const input = form.querySelector('input[type="search"], input[name="q"]');
        if (!input) return;

        const query = input.value.trim();
        if (!query) return;

        send(ENDPOINTS.search, {
            query,
            page: window.location.pathname,
            url: window.location.href,
            referrer: document.referrer || ""
        });

    }, true);

    // =========================
    // FUNNEL TRACKING
    // =========================
    function trackFunnel(data = {}) {

        if (!data.funnel_name) return;

        send(ENDPOINTS.funnel, {
            funnel_name: data.funnel_name,
            step_number: data.step_number ?? null,
            step_name: data.step_name ?? "",
            metadata: data.metadata ?? {},

            page: window.location.pathname,
            url: window.location.href,
            referrer: document.referrer || ""
        });
    }

    window.trackFunnel = trackFunnel;

})();