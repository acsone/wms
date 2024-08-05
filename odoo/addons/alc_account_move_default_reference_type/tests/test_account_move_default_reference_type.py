# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestAccountMoveDefaultReferenceType(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_4")
        cls.partner = cls.env["res.partner"].create({"name": "my test partner"})
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "sale")], limit=1
        )

    @classmethod
    def _create_invoice(cls, partner=None, move_type="out_invoice"):
        if not partner:
            partner = cls.partner
        return cls.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": partner.id,
                "invoice_date": "2020-10-17",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "price_unit": 1000.0,
                            "quantity": 5,
                        }
                    )
                ],
            }
        )

    def test_1(self):
        """Invoice created with the default value structured."""
        out_invoice = out_invoice = self._create_invoice()
        self.assertEqual(self.partner.out_inv_comm_type, "structured")
        self.assertEqual(out_invoice.reference_type, "structured")

    def test_2(self):
        """If no default value, reference type is set to free comm."""
        self.partner.out_inv_comm_type = False
        out_invoice = self._create_invoice()
        self.assertEqual(out_invoice.reference_type, "none")

    def test_3(self):
        """Invoice created with the default value none."""
        self.partner.out_inv_comm_type = "none"
        out_invoice = self._create_invoice()
        self.assertEqual(out_invoice.reference_type, "none")

    def test_4(self):
        """The value set on the commercial partner level is the one used."""
        self.partner.out_inv_comm_type = "none"
        child_partner = self.env["res.partner"].create(
            {"name": "child partner", "parent_id": self.partner.id}
        )
        out_invoice = self._create_invoice(child_partner)
        self.assertEqual(out_invoice.partner_id, child_partner)
        self.assertEqual(child_partner.out_inv_comm_type, "structured")
        self.assertEqual(out_invoice.reference_type, "none")

    def test_5(self):
        """Move_type other than out_invoice and out_refund must have the default value.

        none for reference_type
        """
        self.assertEqual(self.partner.out_inv_comm_type, "structured")
        in_invoice = self._create_invoice(move_type="in_invoice")
        self.assertEqual(in_invoice.reference_type, "none")
        out_refund = self._create_invoice(move_type="out_refund")
        self.assertEqual(out_refund.reference_type, "structured")
