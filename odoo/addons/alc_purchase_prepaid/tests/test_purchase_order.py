# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestPurchaseOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.product_1 = cls.env["product.product"].create(
            {"name": "Product 1", "purchase_method": "receive"}
        )

        cls.partner = cls.env.ref("base.res_partner_1")

        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product_1.name,
                            "product_id": cls.product_1.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_qty": 365,
                            "price_unit": 50,
                        },
                    ),
                ],
            }
        )

    def test_po_without_prepayment(self):
        """
        Data:

            A non prepaid PO with 1 line
        Test case:
            Confirm PO and trigger action_create_invoice
        Expected result:
            A UserError is raised saying there is no invoiceable line
        """
        self.assertFalse(self.po.prepayment)
        self.po.button_confirm()
        self.assertEqual(self.po.order_line.qty_to_invoice, 0)
        self.assertEqual(self.po.order_line.qty_invoiced, 0)
        msg = (
            "There is no invoiceable line. If a product has a control policy based "
            "on received quantity, please make sure that a quantity has been "
            "received."
        )
        with self.assertRaises(UserError, msg=msg):
            self.po.action_create_invoice()
        self.po.order_line.qty_received = 10
        self.assertEqual(self.po.order_line.qty_to_invoice, 10)

    def test_po_with_prepayment_before_confirm(self):
        """
        Data:

            A prepaid PO with 1 line
        Test case:
            Confirm PO and trigger action_create_invoice
        Expected result:
            No error raised and the invoice action is returned
        """
        self.po.prepayment = True
        self.po.button_confirm()
        self.assertEqual(self.po.order_line.qty_to_invoice, 365)
        self.assertEqual(self.po.order_line.qty_invoiced, 0)
        bill_action = self.po.action_create_invoice()
        self.assertEqual(self.po.order_line.qty_to_invoice, -365)
        self.assertEqual(self.po.order_line.qty_invoiced, 365)
        self.assertEqual(bill_action["type"], "ir.actions.act_window")
        self.assertEqual(bill_action["name"], "Bills")
        self.assertEqual(bill_action["res_model"], "account.move")
        invoice_line = self.po.order_line.invoice_lines
        self.assertEqual(invoice_line.quantity, 365)

    def test_po_with_prepayment_after_confirm(self):
        """
        Data:

            A PO with 1 line
        Test case:
            Confirm PO then set it prepaid and trigger action_create_invoice
        Expected result:
            No error raised and the invoice action is returned
        """
        self.po.button_confirm()
        self.po.prepayment = True
        self.assertEqual(self.po.order_line.qty_to_invoice, 365)
        self.assertEqual(self.po.order_line.qty_invoiced, 0)
        bill_action = self.po.action_create_invoice()
        self.assertEqual(self.po.order_line.qty_to_invoice, -365)
        self.assertEqual(self.po.order_line.qty_invoiced, 365)
        self.assertEqual(bill_action["type"], "ir.actions.act_window")
        self.assertEqual(bill_action["name"], "Bills")
        self.assertEqual(bill_action["res_model"], "account.move")
        invoice_line = self.po.order_line.invoice_lines
        self.assertEqual(invoice_line.quantity, 365)

    def test_po_with_2_lines(self):
        """
        This test was created after a reported bug because self was used instead of.

        line in purchase_order_line._compute_qty_invoiced when getting product_uom
        Data:
            A prepaid PO with 2 lines having different uom
        Test case:
            Confirm PO
        Expected result:
            The PO is confirmed
        """
        product_2 = self.env["product.product"].create(
            {"name": "Product 2", "purchase_method": "receive"}
        )
        self.po.order_line = [
            Command.create(
                {
                    "name": product_2.name,
                    "product_id": product_2.id,
                    "product_uom": self.env.ref("uom.product_uom_dozen").id,
                    "product_qty": 100,
                    "price_unit": 75,
                },
            ),
        ]
        self.po.prepayment = True
        self.po.button_confirm()
        self.assertEqual(self.po.state, "purchase")
        self.po.order_line._compute_qty_invoiced()
