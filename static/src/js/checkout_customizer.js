/* @odoo-module */
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
 * The script is intentionally written in vanilla DOM so it survives
 * Odoo CSS class changes between versions. We match fields by their
 * `name` attribute, which is stable across releases.
 */

import { publicWidget } from "@web/legacy/js/public/public_widget";

const CheckoutCustomizer = publicWidget.registry.CheckoutCustomizer = publicWidget.Widget.extend({
    selector: "#checkout_customizer_config",
    events: {},

    /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        this._apply();
        // Re-apply on any dynamic form update (e.g. login modal → back to checkout)
        $(document).on("checkout_customizer:reapply", this._apply.bind(this));
        return Promise.resolve();
    },

    /**
     * @override
     */
    destroy: function () {
        $(document).off("checkout_customizer:reapply");
        this._super.apply(this, arguments);
    },

    // ------------------------------------------------------------------
    // Implementation
    // ------------------------------------------------------------------

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

    /**
     * Hide or show the whole wrapper (input + label + error) for a
     * given field name. Works for both the shipping and billing
     * sections of the checkout form.
     */
    _hideFieldByName: function (fieldName, hide) {
        const inputs = document.querySelectorAll(`[name="${fieldName}"]`);
        inputs.forEach((input) => {
            // Walk up to the closest row / div that contains the label.
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
                // Also make the field not required so the form can submit.
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

    /**
     * Restrict the country <select> to a whitelist of IDs and
     * optionally pre-select a default country.
     */
    _filterCountrySelect: function (allowedIds, defaultCountryId) {
        const selects = document.querySelectorAll('select[name="country_id"]');
        selects.forEach((select) => {
            // Save the original list once so we can restore if settings change.
            if (!select.dataset.customizerOriginal) {
                select.dataset.customizerOriginal = "1";
                // Cache original options as a JSON blob.
                const cached = Array.from(select.options).map((o) => ({
                    value: o.value,
                    text: o.text,
                }));
                select.dataset.customizerOptions = JSON.stringify(cached);
            }

            const originalOptions = JSON.parse(select.dataset.customizerOptions || "[]");

            // Reset and rebuild.
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

            // Pick a value to select.
            let targetValue = currentValue;
            if (
                (!targetValue || !allowedIds.includes(String(targetValue))) &&
                defaultCountryId
            ) {
                targetValue = defaultCountryId;
            }
            // Verify the target actually exists in the filtered list.
            const stillExists = Array.from(select.options).some(
                (o) => String(o.value) === String(targetValue)
            );
            if (stillExists) {
                select.value = targetValue;
            }

            // Trigger change so Odoo's own state-filtering code runs.
            select.dispatchEvent(new Event("change", { bubbles: true }));
        });
    },
});

export default CheckoutCustomizer;
