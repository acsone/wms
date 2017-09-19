# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class ImportConfigSettings(models.TransientModel):
    _inherit = 'import.config.settings'

    locale = fields.Char('Locale to format float', default='fr_BE')

    @api.model
    def default_get(self, fields):
        res = super(ImportConfigSettings, self).default_get(fields)

        config_param = self.env['ir.config_parameter']
        if not fields or 'locale' in fields:
            locale = config_param.get_param('import.locale')
            res['locale'] = locale

        return res

    @api.multi
    def set_locale(self):
        self.ensure_one()

        self.env['ir.config_parameter']\
            .set_param('import.locale', self.locale)
