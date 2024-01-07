// Load auto-refresh functionality when page is loaded
window.addEventListener("load", (event) => {
    const cookie_name = "EnableAutoRefresh";
    const cookie_days = 30;
    const timeout_s = 15;
    const checkbox = document.autoRefreshForm.autoRefreshCheckbox;

    // Set checkbox state and run initial timer
    if (getCookie(cookie_name) != "no") {
        checkbox.checked = true;
        autoRefreshTimeout = setInterval(function() {
            window.location.reload(1);
        }, timeout_s * 1000);
    } else {
        checkbox.checked = false;
    }

    // Set checkbox event listener
    checkbox.addEventListener("change", (event) => {
        if (event.currentTarget.checked) {
            autoRefreshTimeout = setInterval(function() {
                window.location.reload(1);
            }, timeout_s * 1000);
            setCookie(cookie_name, "yes", cookie_days);
        } else {
            if (autoRefreshTimeout)
                clearInterval(autoRefreshTimeout);
            setCookie(cookie_name, "no", cookie_days);
        }
    })
});
