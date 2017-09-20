# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class ImportConfigSettings(models.TransientModel):
    _name = 'import.config.settings'
    _inherit = 'res.config.settings'

    import_in_path = fields.Char('Import IN path', required=True)
    import_out_path = fields.Char('Import OUT path', required=True)
    import_failure_path = fields.Char('Import FAILURE path', required=True)

    @api.model
    def default_get(self, fields):
        res = super(ImportConfigSettings, self).default_get(fields)

        config_param = self.env['ir.config_parameter']
        if not fields or 'import_in_path' in fields:
            import_in_path = config_param.get_param('import.import_in_path')
            res['import_in_path'] = import_in_path
        if not fields or 'import_out_path' in fields:
            import_out_path = config_param.get_param('import.import_out_path')
            res['import_out_path'] = import_out_path
        if not fields or 'import_failure_path' in fields:
            import_failure_path = \
                config_param.get_param('import.import_failure_path')
            res['import_failure_path'] = import_failure_path

        return res

    @api.multi
    def set_import_in_path(self):
        self.ensure_one()

        self.env['ir.config_parameter']\
            .set_param('import.import_in_path', self.import_in_path)

    @api.multi
    def set_import_out_path(self):
        self.ensure_one()

        self.env['ir.config_parameter'] \
            .set_param('import.import_out_path', self.import_out_path)

    @api.multi
    def set_import_failure_path(self):
        self.ensure_one()

        self.env['ir.config_parameter'] \
            .set_param('import.import_failure_path', self.import_failure_path)
