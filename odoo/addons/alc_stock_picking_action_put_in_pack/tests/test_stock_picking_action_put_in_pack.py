# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockPickingActionPutInPack(TransactionCase):
    def test_0(self):
        product = self.env["product.product"].create(
            {"name": "Test product 2", "type": "product"}
        )
        stock_location = self.env["stock.warehouse"].search([], limit=1).lot_stock_id
        supplier_location = self.env.ref("stock.stock_location_suppliers")
        picking_type_in = self.env.ref("stock.picking_type_in")
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": picking_type_in.id,
                "location_id": supplier_location.id,
                "location_dest_id": stock_location.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "In product",
                            "product_id": product.id,
                            "location_id": supplier_location.id,
                            "location_dest_id": stock_location.id,
                            "product_uom_qty": 10,
                            "product_uom": product.uom_id.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        self.assertEqual(len(picking.move_line_ids), 1)
        picking.action_set_quantities_to_reservation()
        picking.action_put_in_pack()
        self.assertFalse(picking.move_line_ids.result_package_id)
