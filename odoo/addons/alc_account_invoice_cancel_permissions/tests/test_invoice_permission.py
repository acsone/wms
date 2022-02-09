# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase


class TestInvoicePermission(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestInvoicePermission, cls).setUpClass()
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
        cls.tax_fixed = cls.env["account.tax"].create(
            {
                "sequence": 10,
                "name": "Tax 10.0 (Fixed)",
                "amount": 10.0,
                "amount_type": "fixed",
                "include_base_amount": True,
            }
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )
        cls.invoice1 = cls._create_invoice(cls.partner, cls.p1)

    @classmethod
    def _create_invoice(cls, partner, product, price_unit=100, qty=5, account=None):
        account = account or cls.account
        invoice = cls.env["account.invoice"].create(
            {
                "partner_id": partner.id,
                "account_id": account.id,
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
        invoice.compute_taxes()
        return invoice

    def test_00_cancel_invoice_without_permission(self):
        self.assertEqual(self.invoice1.state, "draft")
        self.assertFalse(
            self.env.user.has_group(
                "alc_account_invoice_cancel_permissions.cancel_invoice_permission"
            )
        )

        with self.assertRaises(AccessError):
            self.invoice1.action_invoice_cancel()

    def test_01_cancel_invoice_with_permission(self):
        self.assertEqual(self.invoice1.state, "draft")
        self.env.user.write(
            {
                "groups_id": [
                    (
                        4,
                        self.ref(
                            "alc_account_invoice_cancel_permissions.cancel_invoice_permission"
                        ),
                    )
                ],
            }
        )
        self.assertTrue(
            self.env.user.has_group(
                "alc_account_invoice_cancel_permissions.cancel_invoice_permission"
            )
        )
        self.invoice1.action_invoice_cancel()
        self.assertEqual(self.invoice1.state, "cancel")

    def test_02_cancel_invoice_with_wrong_state(self):
        self.assertEqual(self.invoice1.state, "draft")
        self.env.user.write(
            {
                "groups_id": [
                    (
                        4,
                        self.ref(
                            "alc_account_invoice_cancel_permissions.cancel_invoice_permission"
                        ),
                    )
                ],
            }
        )
        self.assertTrue(
            self.env.user.has_group(
                "alc_account_invoice_cancel_permissions.cancel_invoice_permission"
            )
        )
        self.invoice1.state = "paid"
        with self.assertRaises(AccessError):
            self.invoice1.action_invoice_cancel()

    def test_03_cancel_invoice_without_permissions_and_wrong_state(self):
        self.assertEqual(self.invoice1.state, "draft")
        self.assertFalse(
            self.env.user.has_group(
                "alc_account_invoice_cancel_permissions.cancel_invoice_permission"
            )
        )
        self.invoice1.state = "paid"
        with self.assertRaises(AccessError):
            self.invoice1.action_invoice_cancel()
