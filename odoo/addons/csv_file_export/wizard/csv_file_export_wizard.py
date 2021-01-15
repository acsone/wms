# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CSVFileExportWizard(models.TransientModel):
    _name = "csv.file.export.wizard"

    export_ids = fields.Many2many("csv.file.export", string="Exports")

    def default_get(self, fields_list=None):
        fields_list = fields_list or {}
        result = super(CSVFileExportWizard, self).default_get(fields_list=fields_list)

        result["export_ids"] = [(6, 0, self.env.context.get("active_ids", []))]

        return result

    @api.multi
    def execute_exports(self):
        self.ensure_one()

        if not self.export_ids:
            raise UserError(_("Please select at least one export"))

        exports = self.env["csv.file.export"].browse(self.export_ids.ids)
        exports.execute_exports()
