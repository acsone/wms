# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression

import odoo.addons.decimal_precision as dp


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    qty_available = fields.Float(
        compute="_compute_qty_available",
        digits=dp.get_precision("Product Unit of Measure"),
        string="Quantity on hand",
    )

    @api.multi
    @api.depends("quant_ids.qty")
    def _compute_qty_available(self):
        """
        This method compute the available quantities into internal location.
        It reuse the same way to compute the domain as for the computation
        of quantities on a product. Therefore, as for the product the result
        can depend of context parameters (warehouse, location, force_company,
        compute_child)
        """
        quant_domain, _move_in_domain, _move_out_domain = self.env[
            "product.product"
        ]._get_domain_locations()
        quant_domain = expression.AND([quant_domain, [("lot_id", "in", self.ids)]])
        StockQuant = self.env["stock.quant"]
        quants_res = {
            item["lot_id"][0]: item["qty"]
            for item in StockQuant.read_group(
                quant_domain, ["lot_id", "qty"], ["lot_id"]
            )
        }
        for record in self:
            record.qty_available = quants_res.get(record.id)
