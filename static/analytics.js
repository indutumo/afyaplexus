// analytics.js

(function () {

    // =========================================
    // ENDPOINTS
    // =========================================
    const ENDPOINTS = {
        click: "/userprofile/track_click/",
        search: "/userprofile/track_search/",
        funnel: "/userprofile/track_funnel/"
    };

    let lastClickTime = 0;

    // =========================================
    // SAFE FETCH
    // =========================================
    async function send(url, data) {

        try {

            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                },
                credentials: "include",
                body: JSON.stringify(data)
            });

            const result = await response.json();

            console.log("Analytics response:", result);

            if (!response.ok) {
                console.error("Analytics error:", result);
            }

        } catch (err) {
            console.error("Analytics failed:", err);
        }
    }

    // =========================================
    // LABEL BUILDER
    // =========================================
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

    // =========================================
    // SELECTOR BUILDER
    // =========================================
    function getSelector(el) {

        if (!el || el.nodeType !== 1) return "";

        if (el.id) {
            return `#${el.id}`;
        }

        let path = [];

        while (el && el.nodeType === 1 && path.length < 5) {

            let selector = el.tagName.toLowerCase();

            if (el.className && typeof el.className === "string") {

                const cls = el.className
                    .trim()
                    .split(/\s+/)[0];

                if (cls) {
                    selector += "." + cls;
                }
            }

            path.unshift(selector);
            el = el.parentElement;
        }

        return path.join(" > ");
    }

    // =========================================
    // DEVICE INFO
    // =========================================
    function getDeviceInfo() {

        const ua = navigator.userAgent || "";

        // Device type
        let device_type = "desktop";

        if (/Mobi|Android|iPhone|iPod/i.test(ua)) {
            device_type = /iPad/i.test(ua)
                ? "tablet"
                : "mobile";
        }

        // Browser
        let browser = "unknown";

        if (ua.includes("Chrome") && !ua.includes("Edg")) {
            browser = "chrome";
        }
        else if (ua.includes("Firefox")) {
            browser = "firefox";
        }
        else if (ua.includes("Safari") && !ua.includes("Chrome")) {
            browser = "safari";
        }
        else if (ua.includes("Edg")) {
            browser = "edge";
        }

        // OS
        let os = "unknown";

        if (ua.includes("Windows")) {
            os = "windows";
        }
        else if (ua.includes("Mac OS")) {
            os = "macos";
        }
        else if (ua.includes("Android")) {
            os = "android";
        }
        else if (
            ua.includes("iPhone") ||
            ua.includes("iPad") ||
            ua.includes("iOS")
        ) {
            os = "ios";
        }
        else if (ua.includes("Linux")) {
            os = "linux";
        }

        return {
            device_type,
            browser,
            os
        };
    }

    // =========================================
    // COMMON PAGE DATA
    // =========================================
    function getPageData() {

        return {
            page: window.location.pathname,
            page_title: document.title,
            url: window.location.href,
            referrer: document.referrer || "",

            screen_width: window.innerWidth,
            screen_height: window.innerHeight,

            language: navigator.language || "",

            timezone:
                Intl.DateTimeFormat()
                    .resolvedOptions()
                    .timeZone || ""
        };
    }

    // =========================================
    // CLICK TRACKING
    // =========================================
    document.addEventListener("click", function (e) {

        const now = Date.now();

        // Prevent spam clicks
        if (now - lastClickTime < 200) {
            return;
        }

        lastClickTime = now;

        const el = e.target;

        if (!el) return;

        if (
            el.tagName === "HTML" ||
            el.tagName === "BODY"
        ) {
            return;
        }

        const isTrackedButton =
            el.dataset?.trackEvent === "true";

        const device = getDeviceInfo();

        send(ENDPOINTS.click, {

            // Page
            ...getPageData(),

            // Event
            event_type:
                isTrackedButton
                    ? "button_click"
                    : "click",

            label: getLabel(el),

            // Element
            element_type: el.tagName || "",
            element_id: el.id || "",

            css_class:
                typeof el.className === "string"
                    ? el.className
                    : "",

            selector: getSelector(el),

            // Position
            x: e.clientX,
            y: e.clientY,

            // Device
            device_type: device.device_type,
            browser: device.browser,
            os: device.os
        });

    }, true);

    // =========================================
    // SEARCH TRACKING
    // =========================================
    document.addEventListener("submit", function (e) {

        const form = e.target;

        if (!form) return;

        const input = form.querySelector(
            'input[type="search"], input[name="q"]'
        );

        if (!input) return;

        const query = input.value.trim();

        if (!query) return;

        send(ENDPOINTS.search, {

            query,

            ...getPageData()
        });

    }, true);

    // =========================================
    // FUNNEL TRACKING
    // =========================================
    function trackFunnel(data = {}) {

        // Validation
        if (!data.funnel_name) {
            console.error(
                "trackFunnel: funnel_name missing"
            );
            return;
        }

        if (
            data.step_number === undefined ||
            data.step_number === null
        ) {
            console.error(
                "trackFunnel: step_number missing"
            );
            return;
        }

        if (!data.step_name) {
            console.error(
                "trackFunnel: step_name missing"
            );
            return;
        }

        send(ENDPOINTS.funnel, {

            funnel_name: data.funnel_name,
            step_number: Number(data.step_number),
            step_name: data.step_name,

            metadata: data.metadata || {},

            ...getPageData()
        });
    }

    // =========================================
    // GLOBAL ACCESS
    // =========================================
    window.trackFunnel = trackFunnel;

    // =========================================
    // OPTIONAL AUTO PAGE VIEW FUNNEL
    // =========================================
    /*
    trackFunnel({
        funnel_name: "site_visit",
        step_number: 1,
        step_name: "page_loaded"
    });
    */

})();