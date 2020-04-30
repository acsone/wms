# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class PrintingPrinter(models.Model):
    _inherit = 'printing.printer'

    code = fields.Char()
    type = fields.Selection(
        [('zebra', 'Zebra'), ('pdf', 'PDF'), ('toshiba', 'Toshiba')],
        string='Type',
    )

    _sql_constraints = [
        (
            'unique_printer_code_by_type',
            'unique(code, type)',
            _('The printer code must be unique by type'),
        )
    ]
