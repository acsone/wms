# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestStockMove(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockMove, cls).setUpClass()

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

        cls.env.user.company_id.restocking_fee_product_id = cls.env.ref(
            "sale_stock_restocking_fee_invoicing." "product_restocking_fee"
        )

        cls.partner = cls.env["res.partner"].create(
            {"name": "Partner", "charge_restocking_fee": False}
        )
        # Check the case of main and additional products
        cls.additional_product = cls.env["product.product"].create(
            {
                "name": "Additional product",
                "default_code": "987654321",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        update_qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.additional_product.id,
                "product_tmpl_id": cls.additional_product.product_tmpl_id.id,
                "new_quantity": 15,
                "location_id": cls.warehouse_1.lot_stock_id.id,
            }
        )
        update_qty_wizard.change_product_qty()

        cls.main_product = cls.env["product.product"].create(
            {
                "name": "Test medoc 1",
                "default_code": "1234567",
                "tracking": "none",
                "list_price": 100,
                "type": "product",
                "additional_product_id": cls.additional_product.id,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "ratio_main_product": 1,
                "ratio_additional_product": 1,
            }
        )
        update_qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.main_product.id,
                "product_tmpl_id": cls.main_product.product_tmpl_id.id,
                "new_quantity": 100,
                "location_id": cls.warehouse_1.lot_stock_id.id,
            }
        )
        update_qty_wizard.change_product_qty()

        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.main_product.name,
                            "product_id": cls.main_product.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.main_product.uom_id.id,
                        },
                    )
                ],
            }
        )
        cls.so.action_confirm()

        # cls.picking = cls.so.picking_ids
        cls.picking = cls.so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        cls.shipping = cls.so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        cls._process_picking(cls.picking)
        cls._process_picking(cls.shipping)

    @staticmethod
    def _process_picking(picking):
        picking.force_assign()
        for pack in picking.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        picking.do_transfer()

    def _create_return_wizard(self):
        default_data = (
            self.env["stock.return.picking"]
            .with_context(active_ids=self.shipping.ids, active_id=self.shipping.ids[0])
            .default_get(
                [
                    "move_dest_exists",
                    "original_location_id",
                    "product_return_moves",
                    "parent_location_id",
                    "location_id",
                    "charge_restocking_fee",
                ]
            )
        )
        return (
            self.env["stock.return.picking"]
            .with_context(active_ids=self.shipping.ids, active_id=self.shipping.ids[0])
            .create(default_data)
        )

    def _create_return_picking(self):
        res = self._create_return_wizard().create_returns()
        return self.env["stock.picking"].browse(res["res_id"])

    def test_00(self):
        """
        Data:
            A customer charged with restocking fee
            A delivered SO with 2 lines, main and additional products
        Test case:
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            1 new lines for customer fees must be added to the SO
            (only one for the main product) with qty 1
        """

        # Check the additional product is on the picking
        self.assertEqual(len(self.picking.move_lines), 2)
        self.assertEqual(len(self.picking.pack_operation_ids), 2)

        # Check that the additional product is also added to the shipping after confirmation
        self.assertEqual(len(self.shipping.move_lines), 2)

        self.partner.charge_restocking_fee = True

        wizard = self._create_return_wizard()
        self.assertTrue(wizard.is_customer_return)
        self.assertTrue(wizard.charge_restocking_fee)
        res = wizard.create_returns()
        picking = self.env["stock.picking"].browse(res["res_id"])

        self._process_picking(picking)
        # One line for main product, one for return
        self.assertEqual(2, len(self.so.order_line))

        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(1, len(fees_line))
