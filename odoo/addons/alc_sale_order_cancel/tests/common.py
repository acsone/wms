# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleOrderCancelBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "partner"})

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"
        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.product = cls.env["product.product"].create(
            {"name": "product", "type": "product"}
        )
        cls.env["stock.quant"]._update_available_quantity(cls.product, cls.loc_stock, 5)
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 5,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )
        cls.so.action_confirm()
        cls.pick = cls.so.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "internal"
        )
        cls.out = cls.so.picking_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )

    @classmethod
    def _do_transfer(cls, pick):
        pick.action_set_quantities_to_reservation()
        pick._action_done()
