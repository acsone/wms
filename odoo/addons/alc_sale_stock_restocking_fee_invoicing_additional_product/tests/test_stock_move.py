# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests.common import Form, TransactionCase


class TestStockMove(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "ship_only",
                "code": "TST",
            }
        )
        cls.loc_stock = cls.warehouse_1.lot_stock_id
        cls.warehouse_1.out_type_id.allow_additional_product_on_reserved_qty = True

        cls.env.user.company_id.restocking_fee_product_id = cls.env.ref(
            "sale_stock_restocking_fee_invoicing.product_restocking_fee"
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
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.additional_product, cls.loc_stock, 15
        )

        cls.main_product = cls.env["product.product"].create(
            {
                "name": "Test medoc 1",
                "default_code": "1234567",
                "tracking": "none",
                "list_price": 100,
                "type": "product",
                "additional_product_id": cls.additional_product.id,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "ratio_main_product": 1,
                "ratio_additional_product": 1,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.main_product, cls.loc_stock, 100
        )

        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "order_line": [
                    Command.create(
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

        cls.picking = cls.so.picking_ids
        cls._process_picking(cls.picking)

    @staticmethod
    def _process_picking(picking):
        picking.action_assign()
        for ml in picking.move_line_ids:
            ml.qty_done = ml.reserved_qty
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

            A customer charged with restocking fee
            A delivered SO with product main having additional product
        Test case:
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            1 new lines for customer fees must be added to the SO
            (only one for the main product) with qty 1
        """
        self.partner.charge_restocking_fee = True
        # One line for main product, one for additional product
        self.assertEqual(
            2, len(self.picking.move_ids.filtered(lambda move: move.state != "cancel"))
        )

        wizard = self._create_return_wizard()
        self.assertTrue(wizard.is_customer_return)
        self.assertTrue(wizard.charge_restocking_fee)
        res = wizard.create_returns()
        picking = self.env["stock.picking"].browse(res["res_id"])

        self._process_picking(picking)
        # One line for main product, one line for additional, one for return
        self.assertEqual(3, len(self.so.order_line))

        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(1, len(fees_line))
