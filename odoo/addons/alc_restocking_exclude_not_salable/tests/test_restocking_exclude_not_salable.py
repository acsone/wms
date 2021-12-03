# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestRestockingExcludeNotSalable(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestRestockingExcludeNotSalable, cls).setUpClass()

        cls.partner = cls.env["res.partner"].create({"name": "Partner"})

        cls.product_categ = cls.env["product.category"].create(
            {"name": "Test category"}
        )

        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "test product 1",
                "list_price": 20,
                "type": "product",
                "sale_ok": True,
                "active": False,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "test product 2",
                "list_price": 30,
                "type": "product",
                "sale_ok": True,
                "active": True,
            }
        )

        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "test product 3",
                "list_price": 40,
                "type": "product",
                "sale_ok": False,
                "active": True,
            }
        )

        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product_1.name,
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.product_1.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product_2.name,
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 15.0,
                            "product_uom": cls.product_2.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product_3.name,
                            "product_id": cls.product_3.id,
                            "product_uom_qty": 10.0,
                            "product_uom": cls.product_3.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.so.action_confirm()

        cls.picking = cls.so.picking_ids
        cls._process_picking(cls.picking)

    @staticmethod
    def _process_picking(picking):
        picking.force_assign()
        for pack in picking.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        picking.do_transfer()

    def _create_return_wizard(self):
        default_data = (
            self.env["stock.return.picking"]
            .with_context(active_ids=self.picking.ids, active_id=self.picking.ids[0])
            .default_get(
                [
                    "move_dest_exists",
                    "original_location_id",
                    "product_return_moves",
                    "parent_location_id",
                    "location_id",
                    "archived_product",
                ]
            )
        )
        return (
            self.env["stock.return.picking"]
            .with_context(active_ids=self.picking.ids, active_id=self.picking.ids[0])
            .create(default_data)
        )

    def _create_return_picking(self):
        res = self._create_return_wizard().create_returns()
        return self.env["stock.picking"].browse(res["res_id"])

    def test_00(self):
        """
        Data:
            3 products for start, one in an archived lot
        Test case:
            Create a stock return wizard
        Expected result:
            The stock return must:
             * exclude the product marked as archived
             * have only 2 products to return
             * display the error in the html
        """
        wizard = self._create_return_wizard()
        self.assertEqual(len(wizard.product_return_moves), 2)

        product_ids_to_return = [
            product.product_id.id for product in wizard.product_return_moves
        ]
        self.assertFalse(self.product_1.id in product_ids_to_return)

    def test_01(self):
        """
        Data:
            3 products for start, one in an archived lot, another one is flagged sale_ok=False
        Test case:
            Create a stock return wizard
        Expected result:
            The stock return must:
             * exclude the product marked as archived
             * signal the sale_ok = False
             * have only 1 products to return
        """
        wizard = self._create_return_wizard()
        self.assertEqual(len(wizard.product_return_moves), 2)

        not_salable_product = [
            product.not_salable_product for product in wizard.product_return_moves
        ]
        # First one is still sold => product still salable
        self.assertFalse(not_salable_product[0])

        # Second one is not sold anymore => not salable = True
        self.assertTrue(not_salable_product[1])
