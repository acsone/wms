# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class ImportConfigSettings(models.TransientModel):
    _name = 'import.config.settings'
    _inherit = 'res.config.settings'

    import_path = fields.Char('Export path', required=True)
    export_encoding = fields.Char('Export encoding',
                                  required=True,
                                  default='utf-8')

    @api.model
    def default_get(self, fields):
        res = super(ImportConfigSettings, self).default_get(fields)

        config_param = self.env['ir.config_parameter']
        if not fields or 'import_path' in fields:
            export_path = config_param.get_param('import.import_path')
            res['import_path'] = export_path

        return res

    @api.multi
    def set_import_path(self):
        self.ensure_one()

        self.env['ir.config_parameter']\
            .set_param('import.import_path', self.import_path)
