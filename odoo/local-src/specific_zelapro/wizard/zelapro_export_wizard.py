# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ZelaproExportWizard(models.TransientModel):
    _name = 'zelapro.export.wizard'

    export_ids = fields.Many2many('zelapro.export', string='Exports')

    def default_get(self, fields_list={}):
        result = super(ZelaproExportWizard, self)\
            .default_get(fields_list=fields_list)

        result['export_ids'] = [(6, 0, self.env.context.get('active_ids', []))]

        return result

    @api.multi
    def execute_exports(self):
        self.ensure_one()

        if not self.export_ids:
            raise UserError(_('Please select at least one export'))

        exports = self.env['zelapro.export'].browse(self.export_ids.ids)
        exports.execute_exports()
