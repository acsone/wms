# © 2017 Jacques-Etienne Baudoux (BCIM)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from os.path import exists as pexists
from shutil import copyfile

from odoo import _, fields

from odoo.addons.base_report_to_printer.models.printing_printer import (
    PrintingPrinter as PrintingPrinterBase,
)

_logger = logging.getLogger(__name__)


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

    def print_file(self, file_name, report=None, **print_opts):
        """Override for debugging purpose."""
        if pexists(file_name):
            dst_name = f"{file_name}_odoo_print"
            copyfile(file_name, dst_name)
            _logger.info(
                "ALC_PRINTING_BASE: file sent to the printer copied in %s", dst_name
            )
        return super().print_file(file_name=file_name, report=report, **print_opts)
