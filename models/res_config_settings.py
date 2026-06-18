# -*- coding: utf-8 -*-
import json
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # ----- checkout form toggles -----
    checkout_hide_city = fields.Boolean(
        string='Hide City Field',
        help="When enabled, the City input is removed from the website "
             "checkout form (view inheritance, no JS hack).",
        config_parameter='website_sale_checkout_customizer.checkout_hide_city',
    )
    checkout_hide_zip = fields.Boolean(
        string='Hide Zip / Postal Code Field',
        help="When enabled, the Zip / Postal Code input is removed from "
             "the website checkout form (view inheritance, no JS hack).",
        config_parameter='website_sale_checkout_customizer.checkout_hide_zip',
    )
    checkout_hide_company_name = fields.Boolean(
        string='Hide Company Name Field',
        help="When enabled, the Company Name input is removed from the "
             "website checkout form. Useful for B2C stores where the "
             "Company Name field is shown by default due to B2B settings.",
        config_parameter='website_sale_checkout_customizer.checkout_hide_company_name',
    )

    # ----- country restriction -----
    # NOTE: Many2many TIDAK boleh pakai config_parameter= (Odoo 17 hanya
    # mengizinkan boolean/integer/float/char/selection/many2one/datetime).
    # Persistence ditangani manual di get_values() / set_values() bawah.
    checkout_allowed_country_ids = fields.Many2many(
        comodel_name='res.country',
        string='Allowed Countries',
        help="Restrict the country dropdown on the checkout form to this "
             "list. Leave empty to show all countries.",
        domain="[('state_ids', '!=', False)]",
    )
    checkout_default_country_id = fields.Many2one(
        comodel_name='res.country',
        string='Default Country',
        help="Pre-selected country when the checkout form is opened.",
        config_parameter='website_sale_checkout_customizer.checkout_default_country_id',
    )

    # ------------------------------------------------------------------
    # Override get/set so that Many2many / Many2one config parameters
    # are serialized properly (Odoo only handles scalar fields natively
    # via config_parameter).
    # ------------------------------------------------------------------
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        IrConfig = self.env['ir.config_parameter'].sudo()
        allowed_ids = IrConfig.get_param(
            'website_sale_checkout_customizer.checkout_allowed_country_ids', default='')
        default_country_id = IrConfig.get_param(
            'website_sale_checkout_customizer.checkout_default_country_id', default='')
        try:
            allowed_ids_list = [int(i) for i in allowed_ids.split(',') if i.strip().isdigit()] \
                if allowed_ids else []
        except (ValueError, AttributeError):
            allowed_ids_list = []
        try:
            default_country_id = int(default_country_id) if default_country_id else False
        except (ValueError, TypeError):
            default_country_id = False
        res.update(
            checkout_allowed_country_ids=[(6, 0, allowed_ids_list)],
            checkout_default_country_id=default_country_id or False,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        IrConfig = self.env['ir.config_parameter'].sudo()
        allowed = ','.join(str(i) for i in self.checkout_allowed_country_ids.ids)
        IrConfig.set_param(
            'website_sale_checkout_customizer.checkout_allowed_country_ids', allowed)
        IrConfig.set_param(
            'website_sale_checkout_customizer.checkout_default_country_id',
            self.checkout_default_country_id.id or '')
