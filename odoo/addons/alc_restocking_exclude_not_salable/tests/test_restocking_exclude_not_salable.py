# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests.common import Form, TransactionCase


class TestRestockingExcludeNotSalable(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.loc_stock = cls.env.ref("stock.stock_location_stock")
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "test product 1",
                "type": "product",
                "sale_ok": True,
                "active": False,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "test product 2",
                "type": "product",
                "sale_ok": True,
                "active": True,
            }
        )
        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "test product 3",
                "type": "product",
                "sale_ok": False,
                "active": True,
            }
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.picking_type.id,
                "location_id": cls.loc_stock.id,
                "location_dest_id": cls.loc_customer.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "test move p1",
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 5,
                            "location_id": cls.loc_stock.id,
                            "location_dest_id": cls.loc_customer.id,
                        },
                    ),
                    Command.create(
                        {
                            "name": "test move p2",
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 6,
                            "location_id": cls.loc_stock.id,
                            "location_dest_id": cls.loc_customer.id,
                        },
                    ),
                    Command.create(
                        {
                            "name": "test move p3",
                            "product_id": cls.product_3.id,
                            "product_uom_qty": 7,
                            "location_id": cls.loc_stock.id,
                            "location_dest_id": cls.loc_customer.id,
                        },
                    ),
                ],
            }
        )
        cls._process_picking(cls.picking)

    @staticmethod
    def _process_picking(picking):
        picking.action_confirm()
        for move in picking.move_ids:
            move.quantity_done = move.product_qty
        picking.button_validate()

    def _create_return_wizard(self):
        return_wizard = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=self.picking.ids,
                active_id=self.picking.ids[0],
                active_model="stock.picking",
            )
        )
        res = return_wizard.save()
        return res

    def _create_return_picking(self):
        res = self._create_return_wizard().create_returns()
        return self.env["stock.picking"].browse(res["res_id"])

    def test_00(self):
        """
        Data:

            3 products for start, one is archived (product_1), one is not salable
            (product_3)
        Test case:
            Create a stock return wizard
        Expected result:
            The stock return must:
             * exclude the product marked as archived (product_1)
             * have only 2 products to return
             * move for product_3 should be marked not_salable
             * display the exclusion in the html which must contains the display_name
               of the excluded product (product_1)
        """
        wizard = self._create_return_wizard()
        wizard._onchange_picking_id()
        # check only 2 products to return
        self.assertEqual(len(wizard.product_return_moves), 2)
        # check that product_1 is excluded from return lines
        self.assertNotIn(
            self.product_1, wizard.product_return_moves.mapped("product_id")
        )
        # check that move for product_3 is marked not_salable
        not_salable_product = [
            move.product_id
            for move in wizard.product_return_moves
            if move.not_salable_product
        ]
        self.assertEqual(len(not_salable_product), 1)
        self.assertIn(self.product_3, not_salable_product)
        # check the html message which must contain product_1.display_name
        self.assertIn(
            "The following products have been archived and cannot be returned:",
            wizard.archived_products_message,
        )
        self.assertIn(self.product_1.display_name, wizard.archived_products_message)
