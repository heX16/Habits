/**
 * Long-poll connection monitor.
 * Keeps an open connection to /api/keepalive and exposes a global `offline` flag.
 * Requires CONNECTION_CHECK_INTERVAL_MIN from constants.js.
 * Uses NotificationManager from notifications.js when available.
 */
// Global connectivity flag (false = online)
var offline = false;

(function () {
    'use strict';

    if (typeof CONNECTION_CHECK_INTERVAL_MIN === 'undefined' ||
        !CONNECTION_CHECK_INTERVAL_MIN ||
        CONNECTION_CHECK_INTERVAL_MIN <= 0) {
        // Feature disabled
        return;
    }

    // Resolve /api/keepalive relative to constants.js (.../js/constants.js),
    // so it works from pages at any depth and under a reverse-proxy prefix.
    function resolveKeepaliveUrl() {
        const scripts = document.getElementsByTagName('script');
        for (let i = 0; i < scripts.length; i++) {
            const src = scripts[i].src;
            if (src && src.indexOf('/js/constants.js') !== -1) {
                return src.replace(/\/js\/constants\.js.*$/, '/api/keepalive');
            }
        }
        return './api/keepalive';
    }

    const keepaliveUrl = resolveKeepaliveUrl();
    const intervalMs = CONNECTION_CHECK_INTERVAL_MIN * 60 * 1000;
    // Client timeout slightly longer than server hold duration
    const fetchTimeoutMs = intervalMs + 30 * 1000;

    let notifications = null;
    if (typeof NotificationManager !== 'undefined') {
        notifications = new NotificationManager();
    }

    function setOffline(value) {
        const wasOffline = offline;
        offline = value;
        if (value && !wasOffline) {
            showConnectionLostNotification();
        }
    }

    function showConnectionLostNotification() {
        const message = 'Connection to server lost';
        if (notifications) {
            notifications.show(message, 'error');
        } else {
            alert(message);
        }
    }

    function sleep(ms) {
        return new Promise(function (resolve) {
            setTimeout(resolve, ms);
        });
    }

    async function fetchKeepalive() {
        const controller = new AbortController();
        const timeoutId = setTimeout(function () {
            controller.abort();
        }, fetchTimeoutMs);

        try {
            const response = await fetch(keepaliveUrl, {
                method: 'GET',
                cache: 'no-store',
                signal: controller.signal
            });
            if (!response.ok) {
                throw new Error('Keepalive returned status ' + response.status);
            }
            // Consume body so the connection can fully close
            await response.json();
            return true;
        } finally {
            clearTimeout(timeoutId);
        }
    }

    async function connectionMonitorLoop() {
        while (true) {
            try {
                await fetchKeepalive();
                setOffline(false);
                // Successful long-poll finished; open a new one immediately
            } catch (error) {
                // Connection dropped or could not be opened
                try {
                    await fetchKeepalive();
                    setOffline(false);
                } catch (retryError) {
                    setOffline(true);
                    await sleep(intervalMs);
                }
            }
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            connectionMonitorLoop();
        });
    } else {
        connectionMonitorLoop();
    }
})();
