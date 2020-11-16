# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestAssignment(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAssignment, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.operator_user = cls.env["res.users"].create(
            {
                "name": "Operator test",
                "ref": "02984757889392",
                "login": "operator_user_test",
                "operator_code": "99",
                "groups_id": [(4, cls.env.ref("stock.group_stock_user").id)],
                "tz": "Europe/Brussels",
                "lang": "en_US",
                "email": "hello@world.com",
            }
        )

        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest first partner", "ref": "12344566777878"}
        )

        cls.partner2 = cls.env["res.partner"].create(
            {"name": "Unittest second partner", "ref": "12344566777879"}
        )

        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "TST",
            }
        )
        cls.warehouse_1.pick_type_id.subcode = "PICK"

        # Create products
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test medoc 1",
                "default_code": "1234567",
                "tracking": "none",
                "list_price": 100,
                "type": "product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
            }
        )

        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Another product",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "default_code": "567890",
                "tracking": "none",
                "list_price": 100,
                "weight": 20.0,
            }
        )

        cls.picking1 = cls._create_picking(partner=cls.partner1, product=cls.product)
        cls.picking2 = cls._create_picking(partner=cls.partner2, product=cls.product2)

    @classmethod
    def _create_picking(cls, partner=None, warehouse=None, product=None):
        if not partner:
            partner = cls.partner1

        if not warehouse:
            warehouse = cls.warehouse_1

        if not product:
            product = cls.product

        Picking = cls.env["stock.picking"]
        picking_values = {
            "partner_id": partner.id,
            "picking_type_id": warehouse.pick_type_id.id,
            "location_id": cls.env.ref("stock.stock_location_stock").id,
            "location_dest_id": warehouse.wh_output_stock_loc_id.id,
            "move_lines": [
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "picking_type_id": warehouse.pick_type_id.id,
                        "product_uom_qty": 1,
                        "product_uom": product.uom_id.id,
                        "location_id": cls.env.ref("stock.stock_location_stock").id,
                        "location_dest_id": warehouse.wh_output_stock_loc_id.id,
                    },
                )
            ],
        }

        return Picking.create(picking_values)

    def test_cannot_assign_two_picks_to_one_operator(self):
        # Assign the first picking to the first operator
        self.picking1.operator_id = self.operator_user.id

        # Check that the picking is indeed assign to the operator
        self.assertEqual(self.picking1.operator_id.id, self.operator_user.id)

        # Try to assign another picking to the same operator, should throw an error
        self.picking2.operator_id = self.operator_user.id

        # Check that the picking is indeed assign to the operator
        self.assertEqual(self.picking2.operator_id.id, self.operator_user.id)

    def test_operator_is_none_for_both(self):
        self.picking1.operator_id = None
        self.assertFalse(self.picking1.operator_id)

        # None should not be a problem
        self.picking2.operator_id = None
        self.assertFalse(self.picking2.operator_id)
