# -*- coding: utf-8 -*-
{
    'name': 'Website Sale Checkout Customizer',
    'version': '17.0.1.3.1',
    'category': 'Website/Website',
    'summary': 'Hide city/zip/company-name fields and filter allowed countries on website checkout',
    'description': """
Website Sale Checkout Customizer
================================

This module lets you customize the e-commerce checkout form:

* **Server-side removal** of the **Company Name** input field via
  ``ir.ui.view`` inheritance on ``website_sale.address``. The field
  is ABSENT from the rendered HTML on both the create-address page
  (``/shop/address``) and the edit-address page
  (``/shop/address?mode=billing&partner_id=N``) — not merely hidden
  via CSS/JS. (Since v17.0.1.3.0.)
* Hide the **City**, **Zip / Postal Code** fields on the website
  checkout form (JS-based, toggleable from Settings).
* Restrict the **Country** dropdown to a configurable list of allowed
  countries (set in Website Settings).
* Automatically filter the **State / Province** dropdown to match the
  selected country (default Odoo behaviour, but guaranteed because the
  country list is now curated).
* Optional: pre-select a default country on the checkout form.

Configuration
-------------
1. Go to *Website → Configuration → Settings*.
2. Open the *Checkout Customizer* section.
3. Tick *Hide City Field* and / or *Hide Zip Field* as needed.
   (The *Hide Company Name Field* toggle is retained for backwards
   compatibility — Company Name is now ALWAYS removed server-side
   regardless of this toggle, starting from v17.0.1.3.0.)
4. Add the countries you want to allow in *Allowed Countries*.
5. (Optional) Pick a *Default Country* that will be pre-selected on the
   checkout form.

Technical notes
---------------
* Company Name removal: ``ir.ui.view`` inheritance applies an XPath
  ``//div[input[@name='company_name']]`` with ``position="replace"``
  to the ``website_sale.address`` template. This drops the wrapper
  div (label + input + warning small) so the field never reaches the
  browser. Applies to both create and edit modes.
* City / Zip hiding uses a small JS snippet that reads the toggle
  state from a ``data-`` attribute injected by the server, so it
  works even with browser caching.
* Country filtering uses the same JS snippet to filter the
  ``<select name="country_id">`` options client-side.

Author: kelvinzer0
License: LGPL-3
    """,
    'author': 'kelvinzer0',
    'website': 'https://github.com/kelvinzer0',
    'license': 'LGPL-3',
    'depends': [
        'website_sale',
        'website',
        'sales_team',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/website_sale_checkout_views.xml',
    ],
    'assets': {
        'web.assets_frontend_lazy': [
            'website_sale_checkout_customizer/static/src/js/checkout_customizer.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
