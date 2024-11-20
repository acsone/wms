# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command

from odoo.addons.alc_stock_release_channel_assign_blocking_unavailable_product.tests.common import (
    StockReleaseChannelBlockingCommon,
)
from odoo.addons.base.tests.common import BaseCommon


class TestStockPicking(StockReleaseChannelBlockingCommon, BaseCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.route = cls.env.ref("stock.route_warehouse0_mto")

        cls.route.active = True
        cls.warehouse = cls.env.ref("stock.warehouse0")
        # Workaround to get an input movement
        cls.env["stock.rule"].create(
            {
                "name": "Suppliers -> Stock",
                "action": "pull",
                "procure_method": "make_to_stock",
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_dest_id": cls.warehouse.lot_stock_id.id,
                "location_src_id": cls.env.ref("stock.stock_location_suppliers").id,
                "route_id": cls.route.id,
            }
        )
        cls.vendor = cls.env["res.partner"].create(
            {
                "name": "Partner MTO",
            }
        )
        cls.product_mto = cls.env["product.product"].create(
            {
                "name": "Product MTO",
                "type": "product",
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": cls.vendor.id,
                        }
                    )
                ],
            }
        )
        cls.product_mto.route_ids |= cls.route
        cls.sale.write(
            {
                "do_not_deliver_if_alone": False,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product_mto.id,
                            "product_uom_qty": 1.0,
                        }
                    )
                ],
            }
        )

    def test_mto_assign(self):
        """
        Transfer partially the normal product.

        The backorder MTO product move should not require other lines to release
        """
        self.sale.action_confirm()
        self.picking = self.sale.picking_ids.filtered(
            lambda pick: pick.picking_type_code == "outgoing"
        )
        move = self.picking.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        move.quantity_done = 100.0
        self.picking._action_done()
        self.assertEqual(self.picking.state, "done")
        self.backorder = self.picking.backorder_ids
        backorder_move = self.backorder.move_ids.filtered(
            lambda move: move.product_id == self.product
        )
        backorder_move_mto = self.backorder.move_ids.filtered(
            lambda move: move.product_id == self.product_mto
        )
        self.assertTrue(backorder_move.delivery_requires_other_lines)
        self.assertFalse(backorder_move_mto.delivery_requires_other_lines)
        self.assertEqual(backorder_move.product_qty_unavailable, 20)
        self.assertFalse(self.backorder.delivery_requires_other_lines)
        self.assertFalse(self.backorder.blocked_for_channel_assignation)
