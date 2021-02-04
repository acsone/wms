# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AlcLocationContentRelocationGenerator(models.TransientModel):

    _name = "alc.location.content.relocation.generator"

    location_id = fields.Many2one(
        "stock.location", "Location", index=True, required=True
    )

    @api.multi
    def dotransfer(self):
        products = self.location_id.mapped("quant_ids.product_id").with_context(
            location_id=self.location_id
        )

        StockPicking = self.env["stock.picking"]
        stock_location = self.env.ref("stock.stock_location_stock")
        picking_type_id = self.env.ref("stock.picking_type_internal")

        for product in products:
            pick = StockPicking.create(
                {
                    "picking_type_id": picking_type_id.id,
                    "location_id": self.location_id.id,
                    "location_dest_id": stock_location.id,
                    "move_lines": [
                        (
                            0,
                            0,
                            {
                                "name": product.name,
                                "product_id": product.id,
                                "product_uom": product.uom_id.id,
                                "product_uom_qty": product.immediately_usable_qty,
                                "location_id": self.location_id.id,
                                "location_dest_id": stock_location.id,
                            },
                        )
                    ],
                }
            )

            pick.action_assign()
            pick.action_confirm()
            return pick.get_formview_action()
