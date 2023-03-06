# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProduct(TransactionCase):
    @classmethod
    def _get_move_vals(cls, name, qty):
        return {
            "name": name,
            "product_id": cls.product.product_variant_ids.id,
            "product_uom_qty": qty,
            "product_uom": cls.product.uom_id.id,
            "picking_type_id": cls.env.ref("stock.picking_type_in").id,
            "location_id": cls.supplier_location.id,
            "location_dest_id": cls.stock_location.id,
        }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.template"].create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Unittest partner"})
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.pickings = cls.env["stock.picking"].create(
            [
                {
                    "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                    "location_id": cls.supplier_location.id,
                    "location_dest_id": cls.stock_location.id,
                    "partner_id": cls.partner.id,
                    "move_ids": [
                        Command.create(cls._get_move_vals("move 1", 10)),
                        Command.create(cls._get_move_vals("move 2", 5)),
                        Command.create(cls._get_move_vals("move 3", 2)),
                    ],
                },
                {
                    "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                    "location_id": cls.supplier_location.id,
                    "location_dest_id": cls.stock_location.id,
                    "partner_id": cls.partner.id,
                    "move_ids": [
                        Command.create(cls._get_move_vals("move 1", 10)),
                        Command.create(cls._get_move_vals("move 2", 5)),
                        Command.create(cls._get_move_vals("move 3", 2)),
                    ],
                },
            ]
        )
        cls.pickings.action_confirm()
        cls.pickings.action_assign()

    def test_1(self):
        self.product._compute_incoming_pickings()
        # 2 pickings, 6 stock moves, the count should be 2
        self.assertEqual(self.product.count_incoming_moves, 2)
