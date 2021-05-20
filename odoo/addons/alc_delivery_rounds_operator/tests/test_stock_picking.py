# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestStockPicking(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockPicking, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777878"}
        )
        cls.operator_1 = cls.env.user.copy()
        cls.operator_2 = cls.operator_1.copy()
        cls.operators = cls.operator_2 | cls.operator_1
        cls.delivery_template = cls.env["round.template"].create(
            {
                "name": "Unittest delivery template",
                "operator_ids": [(6, 0, cls.operators.ids)],
            }
        )
        cls.round_instance = cls.env["round.instance"].create(
            {"template_id": cls.delivery_template.id, "date": "2017-01-01"}
        )
        cls.no_operator = cls.operator_2.copy()
        cls.env["stock.location"]._parent_store_compute()
        cls.warehouse_1 = cls.env["stock.warehouse"].create(
            {
                "name": "Base Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "BWH",
            }
        )
        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )
        warehouse = cls.warehouse_1
        Picking = cls.env["stock.picking"]
        picking_values = {
            "partner_id": cls.partner1.id,
            "picking_type_id": warehouse.pick_type_id.id,
            "location_id": cls.env.ref("stock.stock_location_stock").id,
            "location_dest_id": warehouse.wh_output_stock_loc_id.id,
            "move_lines": [
                (
                    0,
                    0,
                    {
                        "name": cls.p1.name,
                        "product_id": cls.p1.id,
                        "picking_type_id": warehouse.pick_type_id.id,
                        "product_uom_qty": 1,
                        "product_uom": cls.p1.uom_id.id,
                        "location_id": cls.env.ref("stock.stock_location_stock").id,
                        "location_dest_id": warehouse.wh_output_stock_loc_id.id,
                    },
                )
            ],
        }
        cls.picking = Picking.create(picking_values)
        cls.picking.delivery_round_id = cls.round_instance

    def test_00(self):
        """
            DATA:
                A round instance with 2 operators
                A picking without operator
            Test case:
                1. Assign an operator part of the list of round instance operators
                2. Assign on operator not in the list of round instance operators
            Expected result:
                1. Operator is assigned to the picking
                2. ValidationError is raised
        """
        self.picking.operator_id = self.operator_1
        self.assertEqual(self.picking.operator_id, self.operator_1)
        with self.assertRaises(ValidationError):
            self.picking.operator_id = self.no_operator

    def test_01(self):
        """
            DATA:
                A round instance with 2 operators
                A picking with 1 allowed operator
            Test case:
                Remove the operator linked to the picking from the list of
                operators on the round instance
            Expected result:
                No error is raised ans the operator is still assigned to the
                picking
        """
        self.picking.operator_id = self.operator_1
        self.round_instance.operators_ids = False
        self.assertFalse(self.round_instance.operators_ids)
        self.assertEqual(self.picking.operator_id, self.operator_1)
