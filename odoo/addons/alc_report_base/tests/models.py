# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class TestModel(models.Model):
    _name = "test.model"
    _inherit = ["alc.report.print.async"]  # nosemgrep: is-old-style-inheritance
    _description = "Test model for report async"

    def get_report_name(self):
        return "Test report"
