# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests.common import Form, TransactionCase


class TestRmaSaleStockRestockingFeeInvoicing(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {"name": "Partner", "charge_restocking_fee": False}
        )

        cls.product_categ = cls.env["product.category"].create(
            {"name": "Test category"}
        )

        cls.product_1 = cls.env["product.product"].create(
            {"name": "test product 1", "list_price": 20, "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "test product 2", "list_price": 30, "type": "product"}
        )
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product_1.name,
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.product_1.uom_id.id,
                        },
                    ),
                    Command.create(
                        {
                            "name": cls.product_2.name,
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 15.0,
                            "product_uom": cls.product_2.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.so.action_confirm()
        cls.operation = cls.env.ref("rma.rma_operation_replace")
        cls.operation.action_create_refund = "update_quantity"
        cls.rma_reason = cls.env.ref("rma_reason.rma_reason_defective_product")
        cls.picking = cls.so.picking_ids
        cls._process_picking(cls.picking)

    @staticmethod
    def _process_picking(picking):
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity_done = move.product_qty
        picking.button_validate()

    def _create_return_wizard(self, rma_reason=None):
        return_wizard = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=self.picking.ids,
                active_id=self.picking.ids[0],
                active_model="stock.picking",
            )
        )
        return_wizard.create_rma = True
        return_wizard.rma_operation_id = self.operation
        if rma_reason:
            return_wizard.rma_reason_id = rma_reason
        res = return_wizard.save()
        return res

    def _create_rma_sale_wizard(self, rma_reason=None):
        wizard_id = self.so.action_create_rma()["res_id"]
        wizard = self.env["sale.order.rma.wizard"].browse(wizard_id)
        wizard.operation_id = self.operation
        if rma_reason:
            wizard.reason_id = rma_reason
        return wizard

    def _create_return_picking(self, from_so=False, rma_reason=None):
        if from_so:
            wizard = self._create_rma_sale_wizard(rma_reason=rma_reason)
            self.env["rma"].browse(wizard.create_and_open_rma()["res_id"])
        else:
            wizard = self._create_return_wizard(rma_reason=rma_reason)
            wizard.create_returns()
        return self.picking.move_ids.rma_ids.reception_move_id.picking_id

    def test_01(self):
        """
        Data:

            A customer charged with restocking fee
            A delivered SO with 2 lines
            No rma reason selected
        Test case:
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            No restocking fee
        """
        self.partner.charge_restocking_fee = True
        self.assertEqual(2, len(self.so.order_line))
        picking = self._create_return_picking()
        self.assertEqual(len(self.picking.move_ids.rma_ids), 2)
        self.assertEqual(2, len(self.so.order_line))
        self._process_picking(picking)
        self.assertEqual(2, len(self.so.order_line))
        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(0, len(fees_line))

    def test_02(self):
        """
        Data:

            A customer charged with restocking fee
            A delivered SO with 2 lines
            rma reason selected without restocking fee
        Test case:
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            No restocking fee
        """
        self.partner.charge_restocking_fee = True
        self.assertEqual(2, len(self.so.order_line))
        picking = self._create_return_picking(rma_reason=self.rma_reason)
        self.assertEqual(len(self.picking.move_ids.rma_ids), 2)
        self.assertEqual(2, len(self.so.order_line))
        self._process_picking(picking)
        self.assertEqual(2, len(self.so.order_line))
        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(0, len(fees_line))

    def test_03(self):
        """
        Data:

            A customer charged with restocking fee
            A delivered SO with 2 lines
            rma reason selected with restocking fee
        Test case:
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            2 lines for restocking fee
        """
        self.partner.charge_restocking_fee = True
        self.rma_reason.charge_restocking_fee = True
        self.assertEqual(2, len(self.so.order_line))
        picking = self._create_return_picking(rma_reason=self.rma_reason)
        self.assertEqual(len(self.picking.move_ids.rma_ids), 2)
        self.assertEqual(2, len(self.so.order_line))
        self._process_picking(picking)
        self.assertEqual(4, len(self.so.order_line))
        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(2, len(fees_line))

    def test_04(self):
        """
        Data:

            A customer charged with restocking fee
            A delivered SO with 2 lines
            No rma reason selected
        Test case:
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            No restocking fee
        """
        self.partner.charge_restocking_fee = True
        self.assertEqual(2, len(self.so.order_line))
        picking = self._create_return_picking(from_so=True)
        self.assertEqual(len(self.picking.move_ids.rma_ids), 2)
        self.assertEqual(2, len(self.so.order_line))
        self._process_picking(picking)
        self.assertEqual(2, len(self.so.order_line))
        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(0, len(fees_line))

    def test_05(self):
        """
        Data:

            A customer charged with restocking fee
            A delivered SO with 2 lines
            rma reason selected without restocking fee
        Test case:
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            No restocking fee
        """
        self.partner.charge_restocking_fee = True
        self.assertEqual(2, len(self.so.order_line))
        picking = self._create_return_picking(from_so=True, rma_reason=self.rma_reason)
        self.assertEqual(len(self.picking.move_ids.rma_ids), 2)
        self.assertEqual(2, len(self.so.order_line))
        self._process_picking(picking)
        self.assertEqual(2, len(self.so.order_line))
        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(0, len(fees_line))

    def test_06(self):
        """
        Data:

            A customer charged with restocking fee
            A delivered SO with 2 lines
            rma reason selected with restocking fee
        Test case:
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            2 line for restocking fee
        """
        self.partner.charge_restocking_fee = True
        self.rma_reason.charge_restocking_fee = True
        self.assertEqual(2, len(self.so.order_line))
        picking = self._create_return_picking(from_so=True, rma_reason=self.rma_reason)
        self.assertEqual(len(self.picking.move_ids.rma_ids), 2)
        self.assertEqual(2, len(self.so.order_line))
        self._process_picking(picking)
        self.assertEqual(4, len(self.so.order_line))
        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(2, len(fees_line))
