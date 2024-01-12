# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockPickingActionPutInPack(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        product = cls.env["product.product"].create(
            {"name": "Test product 2", "type": "product"}
        )
        stock_location = cls.env["stock.warehouse"].search([], limit=1).lot_stock_id
        supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type_in.id,
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
        cls.picking.action_confirm()
        cls.picking.action_assign()
        cls.picking.action_set_quantities_to_reservation()
        cls.picking_type_in.set_delivery_package_type_on_put_in_pack = True

    def test_1(self):
        """Make package type selection mandatory even for one move line and no carrier."""
        self.assertFalse(self.picking.carrier_id)
        self.assertFalse(self.picking.ship_carrier_id)
        self.assertEqual(len(self.picking.move_line_ids), 1)
        action = self.picking.action_put_in_pack()
        self.assertFalse(self.picking.move_line_ids.result_package_id)
        self.assertEqual(action.get("res_model"), "choose.delivery.package")
