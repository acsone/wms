# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

from ..utils import hw_print


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def print_product_label(self, quantity=1, printer_id=False):
        self.ensure_one()
        hw_print(
            self,
            "specific_print.report_lot_nolot_label",
            qty=quantity * self.number_labels_to_print,
            printer_id=printer_id,
        )
