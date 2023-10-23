# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.fields import Command
from odoo.tests.common import Form, TransactionCase, users


class TestSerialNumber(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user = cls.env.ref("base.user_demo")
        cls.user.groups_id |= cls.env.ref("stock.group_stock_user")
        cls.stock = cls.env.ref("stock.stock_location_stock")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.wizard_obj = cls.env["modify.serial.number"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "product",
                "route_ids": [Command.set(cls.warehouse.delivery_route_id.ids)],
            }
        )
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product.id,
                "inventory_quantity": 5.0,
                "location_id": cls.stock.id,
            }
        )._apply_inventory()

        cls.env["procurement.group"].run(
            [
                cls.env["procurement.group"].Procurement(
                    cls.product,
                    5.0,
                    cls.product.uom_id,
                    cls.customers,
                    "Test Procurement",
                    "/",
                    cls.env.company,
                    {},
                )
            ]
        )

        cls.picking = cls.env["stock.picking"].search(
            [("product_id", "=", cls.product.id), ("location_id", "=", cls.stock.id)]
        )

    @users("demo")
    def test_serial_number(self):
        action = self.picking.move_ids.button_edit_serial_number()
        self.assertIn("res_model", action)
        self.assertEqual(action.get("res_model"), "modify.serial.number")

    @users("demo")
    def test_show_serial_number(self):
        self.assertFalse(self.picking.move_ids.show_serial_number)
        self.picking.picking_type_id.show_serial_number = True
        self.assertTrue(self.picking.move_ids.show_serial_number)

    @users("demo")
    def test_wizard(self):
        self.assertFalse(self.picking.move_ids.serial_number)
        with Form(
            self.wizard_obj.with_context(active_id=self.picking.move_ids.id)
        ) as wizard_form:
            wizard_form.serial_number = "123456"
        wizard = wizard_form.save()
        wizard.save_new_serial_number()
        self.assertEqual("123456", self.picking.move_ids.serial_number)
        self.assertEqual("123456", self.picking.move_ids.move_dest_ids.serial_number)
