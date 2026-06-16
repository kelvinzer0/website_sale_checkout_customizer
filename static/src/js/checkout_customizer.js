/** @odoo-module **/
/**
 * Website Sale Checkout Customizer
 * --------------------------------
 * Reads configuration injected by the server as `data-` attributes on
 * a hidden input (#checkout_customizer_config) and applies:
 *
 *   - Hide the City input + label
 *   - Hide the Zip / Postal Code input + label
 *   - Restrict the Country <select> to a whitelist of country IDs
 *   - Pre-select a default country when the form is empty
 *   - Re-filter the State / Province dropdown whenever the country
 *     changes (Odoo already does this natively, but we re-trigger it
 *     to be safe after we mutate the country list)
 *
 * IMPORTANT: This module MUST be registered only in
 * `web.assets_frontend_lazy`. If it is registered in
 * `web.assets_frontend` (which becomes `web.assets_frontend_minimal`
 * in Odoo 17), `publicWidget` will not yet be defined when this file
 * executes, causing:
 *   "Cannot read properties of undefined (reading 'registry')"
 *
 * Defensive guard: if `publicWidget` is still undefined when this
 * module loads (rare bundle ordering glitch), we wait for it via
 * polling and register the widget once it becomes available.
 */

import { publicWidget } from "@web/legacy/js/public/public_widget";

const WIDGET_NAME = "CheckoutCustomizer";

function _registerWidget(pw) {
    if (!pw || !pw.registry || pw.registry[WIDGET_NAME]) {
        return true; // already registered or cannot register
    }
    pw.registry[WIDGET_NAME] = pw.Widget.extend({
        selector: "#checkout_customizer_config",
        events: {},

        start: function () {
            this._super.apply(this, arguments);
            this._apply();
            $(document).on("checkout_customizer:reapply", this._apply.bind(this));
            return Promise.resolve();
        },

        destroy: function () {
            $(document).off("checkout_customizer:reapply");
            this._super.apply(this, arguments);
        },

        _apply: function () {
            const cfgEl = document.getElementById("checkout_customizer_config");
            if (!cfgEl) {
                return;
            }

            const hideCity = cfgEl.dataset.hideCity === "1";
            const hideZip = cfgEl.dataset.hideZip === "1";
            const allowedIdsRaw = cfgEl.dataset.allowedCountryIds || "";
            const defaultCountryId = cfgEl.dataset.defaultCountryId || "";

            const allowedIds = allowedIdsRaw
                ? allowedIdsRaw.split(",").map((s) => s.trim()).filter(Boolean).map(String)
                : [];

            this._hideFieldByName("city", hideCity);
            this._hideFieldByName("zip", hideZip);
            this._filterCountrySelect(allowedIds, defaultCountryId);
        },

        _hideFieldByName: function (fieldName, hide) {
            const inputs = document.querySelectorAll(`[name="${fieldName}"]`);
            inputs.forEach((input) => {
                const wrapper =
                    input.closest(".div_" + fieldName) ||
                    input.closest(".row") ||
                    input.closest(".mb-3") ||
                    input.closest("div");
                if (!wrapper) {
                    return;
                }
                if (hide) {
                    wrapper.style.setProperty("display", "none", "important");
                    if (input.hasAttribute("required")) {
                        input.removeAttribute("required");
                        input.dataset.customizerWasRequired = "1";
                    }
                } else {
                    wrapper.style.removeProperty("display");
                    if (input.dataset.customizerWasRequired === "1") {
                        input.setAttribute("required", "required");
                        delete input.dataset.customizerWasRequired;
                    }
                }
            });
        },

        _filterCountrySelect: function (allowedIds, defaultCountryId) {
            const selects = document.querySelectorAll('select[name="country_id"]');
            selects.forEach((select) => {
                if (!select.dataset.customizerOriginal) {
                    select.dataset.customizerOriginal = "1";
                    const cached = Array.from(select.options).map((o) => ({
                        value: o.value,
                        text: o.text,
                    }));
                    select.dataset.customizerOptions = JSON.stringify(cached);
                }

                const originalOptions = JSON.parse(select.dataset.customizerOptions || "[]");
                const currentValue = select.value || defaultCountryId || "";
                select.innerHTML = "";

                originalOptions.forEach((opt) => {
                    const include = allowedIds.length === 0 || allowedIds.includes(String(opt.value));
                    if (!include) {
                        return;
                    }
                    const o = document.createElement("option");
                    o.value = opt.value;
                    o.textContent = opt.text;
                    select.appendChild(o);
                });

                let targetValue = currentValue;
                if (
                    (!targetValue || !allowedIds.includes(String(targetValue))) &&
                    defaultCountryId
                ) {
                    targetValue = defaultCountryId;
                }
                const stillExists = Array.from(select.options).some(
                    (o) => String(o.value) === String(targetValue)
                );
                if (stillExists) {
                    select.value = targetValue;
                }

                select.dispatchEvent(new Event("change", { bubbles: true }));
            });
        },
    });
    return true;
}

// Try to register immediately; if `publicWidget` is somehow undefined
// (which should not happen in `web.assets_frontend_lazy` but we guard
// anyway), poll until it becomes available.
if (!_registerWidget(publicWidget)) {
    let attempts = 0;
    const interval = setInterval(() => {
        attempts += 1;
        if (_registerWidget(publicWidget) || attempts > 50) {
            clearInterval(interval);
        }
    }, 100);
}

export default publicWidget && publicWidget.registry
    ? publicWidget.registry[WIDGET_NAME]
    : null;
