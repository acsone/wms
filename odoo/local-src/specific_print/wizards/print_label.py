# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PrintLabel(models.TransientModel):
    _name = 'print.label'

    label_type = fields.Selection([('product', 'Product'),
                                   ('package', 'Package')],
                                  string='Label type',
                                  required=True)
    printer_number = fields.Char('Printer number')
    picking_id = fields.Many2one('stock.picking', required=True)

    @api.multi
    def print_label(self):
        self.ensure_one()

        printer_number = self.printer_number

        domain = [('code', '=', printer_number)]
        if self.label_type == 'product':
            domain += [('type', '=', 'toshiba')]
        else:
            domain += [('type', '=', 'zebra')]
        printer = self.env['printing.printer'].search(domain)

        if not printer:
            raise UserError(_('Printer not found'))

        if self.label_type == 'product':
            self.picking_id.print_products_label(printer=printer)
        else:
            self.picking_id.print_packages_label(printer=printer)
