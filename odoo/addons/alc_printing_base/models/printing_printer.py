# © 2017 Jacques-Etienne Baudoux (BCIM)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields

from odoo.addons.base_report_to_printer.models.printing_printer import (
    PrintingPrinter as PrintingPrinterBase,
)


class PrintingPrinter(PrintingPrinterBase):

    code = fields.Char()
    type = fields.Selection(
        [("zebra", "Zebra"), ("pdf", "PDF"), ("toshiba", "Toshiba")], string="Type"
    )

    _sql_constraints = [
        (
            "unique_printer_code_by_type",
            "unique(code, type)",
            _("The printer code must be unique by type"),
        )
    ]
