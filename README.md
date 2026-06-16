# Website Sale Checkout Customizer

Odoo 16 module — customize the e-commerce checkout form:

* Hide the **City** input
* Hide the **Zip / Postal Code** input
* Restrict the **Country** dropdown to a configurable whitelist
* Pre-select a **default country**

Built as a clean replacement for a JS hack. All toggles live in
**Website → Configuration → Settings → Checkout Customizer**.

## Requirements

* Odoo 16.0 Community or Enterprise
* Modules installed: `website`, `website_sale`

## Installation

### Option A — Drop into the addons path (bare-metal / VM)

```bash
# 1. Copy the module folder into your Odoo addons path
cp -r website_sale_checkout_customizer /opt/odoo/addons/

# 2. Restart Odoo so it picks up the new module
sudo systemctl restart odoo

# 3. Activate developer mode (Settings → Activate Developer Mode)

# 4. Apps → Update Apps List

# 5. Search "Checkout Customizer" → Install
```

### Option B — Docker / Portainer

If you run Odoo in Docker (e.g. the official `odoo:16` image):

1. **Mount the module as a volume.** Add this to the Odoo container's
   volumes in your `docker-compose.yml`:

   ```yaml
   services:
     odoo:
       image: odoo:16
       volumes:
         - odoo-web-data:/var/lib/odoo
         - ./config:/etc/odoo
         - ./addons:/mnt/extra-addons
         - ./website_sale_checkout_customizer:/mnt/extra-addons/website_sale_checkout_customizer
       ports:
         - "8069:8069"
   ```

   Or, if you already have an `extra-addons` directory mounted, just
   drop the folder there:

   ```bash
   docker cp website_sale_checkout_customizer odoo:/mnt/extra-addons/
   ```

2. **Ensure `addons_path` includes the extra addons.** In your
   `odoo.conf`:

   ```ini
   [options]
   addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
   ```

3. **Restart the container** (via Portainer: *Containers → odoo →
   Restart*), or:

   ```bash
   docker restart odoo
   ```

4. **Update Apps List**:
   * Open Odoo web → Settings → Activate the developer mode.
   * Apps → Update Apps List.

5. **Install**: Search "Checkout Customizer" → click Install.

## Configuration

After install:

1. Go to **Website → Configuration → Settings**.
2. Scroll to the **Checkout Customizer** block.
3. Set:
   * **Hide City Field** — tick to remove City from the form.
   * **Hide Zip / Postal Code Field** — tick to remove Zip.
   * **Allowed Countries** — pick the countries that should appear in
     the checkout dropdown. Leave empty to show all countries.
   * **Default Country** — the country that will be pre-selected when
     the checkout form opens.
4. Click **Save**.

Changes are reflected on the next checkout page load (no Odoo restart
required because config is read from `ir.config_parameter` and
injected as `data-` attributes on each request).

## How it works

| Concern              | Implementation                                                       |
| -------------------- | ------------------------------------------------------------------- |
| Field hiding         | Vanilla JS reads `data-hide-city` / `data-hide-zip` and sets `display:none` on the input wrapper. The original `required` attribute is removed so the form can submit. |
| Country whitelist    | Vanilla JS reads `data-allowed-country-ids` and rebuilds the `<select>` options, then fires a `change` event so Odoo's own state-province filter kicks in. |
| Default country      | If the `<select>` has no current value, the configured default is selected. |
| Settings storage     | `ir.config_parameter` keys, read by `res.config.settings` and the checkout template. |
| Frontend asset load  | JS file added to `web.assets_frontend` via template inheritance — no manual script tag needed. |

## Why this instead of a JS hack in a QWeb template

* Survives Odoo upgrades — uses `name=` attribute selectors, not
  CSS-class selectors (which Odoo changes between versions).
* Centralised config — flip toggles from the Settings UI instead of
  editing code.
* No risk of breaking the form submit — required attributes are
  stripped cleanly when fields are hidden.

## File map

```
website_sale_checkout_customizer/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── res_config_settings.py        # Settings fields + get/set
├── views/
│   ├── res_config_settings_views.xml # Settings UI block
│   ├── website_sale_checkout_views.xml # Data-attribute injector
│   └── assets.xml                    # JS bundle registration
└── static/
    └── src/
        ├── js/checkout_customizer.js # Frontend logic
        └── scss/checkout_customizer.scss
```

## Uninstall

1. Apps → search "Checkout Customizer" → Uninstall.
2. The `ir.config_parameter` keys are automatically removed with the
   module's records.

## License

LGPL-3

## Author

kelvinzer0 — https://github.com/kelvinzer0
