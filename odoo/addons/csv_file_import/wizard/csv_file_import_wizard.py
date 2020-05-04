# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CSVFileImportWizard(models.TransientModel):
    _name = "csv.file.import.wizard"

    import_ids = fields.Many2many("csv.file.import", string="Imports")

    def default_get(self, fields_list={}):
        result = super(CSVFileImportWizard, self).default_get(fields_list=fields_list)

        result["import_ids"] = [(6, 0, self.env.context.get("active_ids", []))]

        return result

    @api.multi
    def execute_imports(self):
        self.ensure_one()

        if not self.import_ids:
            raise UserError(_("Please select at least one import"))

        imports = self.env["csv.file.import"].browse(self.import_ids.ids)
        imports.execute_imports()
