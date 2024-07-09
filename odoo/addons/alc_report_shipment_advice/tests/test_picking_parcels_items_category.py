# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPickingTotal(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_obj = cls.env["product.product"]
        cls.advice_obj = cls.env["shipment.advice"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.warehouse.delivery_steps = "pick_ship"
        cls.stock = cls.warehouse.lot_stock_id
        cls.wizard_obj = cls.env["choose.delivery.package"]
        cls.medocs = cls.env["stock.package.type.category"].create(
            {
                "name": "Médicaments",
                "code": "MED",
            }
        )
        cls.aliments = cls.env["stock.package.type.category"].create(
            {
                "name": "Aliments",
                "code": "ALI",
            }
        )
        cls.boite_medocs = cls.env["stock.package.type"].create(
            {
                "name": "Boîte Médicaments",
                "category_id": cls.medocs.id,
            }
        )
        cls.boite_aliments = cls.env["stock.package.type"].create(
            {
                "name": "Boîte Aliments",
                "category_id": cls.medocs.id,
            }
        )
        cls.product = cls.product_obj.create(
            {
                "name": "Product 1 Test",
                "type": "product",
                "route_ids": [Command.link(cls.warehouse.delivery_route_id.id)],
            }
        )
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product.id,
                "location_id": cls.stock.id,
                "inventory_quantity": 10.0,
            }
        )._apply_inventory()

    def test_delivery(self):
        proc_vals = {}
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product,
                    5.0,
                    self.product.uom_id,
                    self.customers,
                    "Test 1",
                    "Test 1",
                    self.env.company,
                    proc_vals,
                ),
            ]
        )
        pick_move = self.env["stock.move"].search(
            [("product_id", "=", self.product.id), ("location_id", "=", self.stock.id)]
        )
        self.assertTrue(pick_move)

        pick_move

        wizard = self.wizard_obj.create(
            {
                "picking_id": pick_move.picking_id.id,
                "delivery_package_type_id": self.boite_medocs.id,
            }
        )
        wizard.action_put_in_pack()

        self.assertTrue(pick_move.move_line_ids.result_package_id)

        pick_move.picking_id._action_done()

        ship_move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product.id),
                ("location_dest_id", "=", self.customers.id),
            ]
        )
        self.assertTrue(pick_move)

        advice = self.advice_obj.create(
            {
                "name": "Test",
                "shipment_type": "outgoing",
            }
        )

        ship_move.picking_id._load_in_shipment(advice)
        result = advice.get_alc_report_shipment_advice()
        print(result)
