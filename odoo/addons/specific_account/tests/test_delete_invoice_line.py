# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo.tests.common import SavepointCase


class TestDeleteInvoiceLine(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestDeleteInvoiceLine, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "Unittest tax",
                "price_include": False,
                "amount_type": "percent",
                "amount": "10",
            }
        )
        cls.p1 = cls.env["product.product"].create(
            {"name": "Unittest P1", "taxes_id": [(6, False, [cls.tax.id])]}
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "84023435243"}
        )
        cls.account_type = cls.env["account.account.type"].create(
            {"name": "Test", "type": "receivable"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )
        cls.invoice = cls.env["account.invoice"].create(
            {
                "partner_id": cls.partner.id,
                "account_id": cls.account.id,
                "invoice_line_ids": [
                    (
                        0,
                        False,
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p1.id,
                            "quantity": 1,
                            "uom_id": cls.env.ref("product.product_uom_unit").id,
                            "price_unit": 100.0,
                            "account_id": cls.account.id,
                        },
                    )
                ],
            }
        )
        cls.invoice.invoice_line_ids._set_taxes()
        cls.invoice.compute_taxes()

    def test_taxes_computation_on_invoice_line_delete(self):
        """Check taxes on the invoice are updated when deleting a line."""
        self.assertEqual(len(self.invoice.invoice_line_ids), 1)
        self.assertEqual(len(self.invoice.tax_line_ids), 1)
        self.assertTrue(self.invoice.amount_tax)
        self.invoice.with_context(recompute_taxes_on_delete=True).invoice_line_ids = [
            (5, False, False)
        ]
        self.assertEqual(len(self.invoice.invoice_line_ids), 0)
        self.assertEqual(len(self.invoice.tax_line_ids), 0)
        self.assertEqual(self.invoice.amount_tax, 0)
