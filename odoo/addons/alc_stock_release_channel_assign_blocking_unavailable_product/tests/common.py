# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command


class StockReleaseChannelBlockingCommon:

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "product", "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "product 2", "type": "product"}
        )
        cls.wh = cls.env.ref("stock.warehouse0")
        cls.loc_stock = cls.wh.lot_stock_id
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.loc_stock, 100.0
        )
        cls.partner = cls.env["res.partner"].create({"name": "Unittest partner"})
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 120,
                        },
                    )
                ],
            }
        )

    @classmethod
    def _do_picking(cls, picking, done_qty):
        picking.move_ids.quantity_done = done_qty
        picking._action_done()
