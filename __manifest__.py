# -*- coding: utf-8 -*-
{
    'name': 'Website Sale Checkout Customizer',
    'version': '17.0.1.2.1',
    'category': 'Website/Website',
    'summary': 'Hide city/zip/company-name fields and filter allowed countries on website checkout',
    'description': """
Website Sale Checkout Customizer
================================

This module lets you customize the e-commerce checkout form:

* Hide the **City**, **Zip / Postal Code**, and **Company Name** input
  fields on the website checkout form (view inheritance, survives
  Odoo upgrades).
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
3. Tick *Hide City Field*, *Hide Zip Field*, and / or
   *Hide Company Name Field*.
4. Add the countries you want to allow in *Allowed Countries*.
5. (Optional) Pick a *Default Country* that will be pre-selected on the
   checkout form.

Technical notes
---------------
* Field hiding uses ``ir.ui.view`` inheritance on
  ``website_sale.website_sale_checkout_form`` — no JS hacks, survives
  upgrades.
* Country filtering uses a small JS snippet that reads the allowed list
  from a ``data-`` attribute injected by the server, so it works even
  with browser caching.

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
