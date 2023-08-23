# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestPartnerInvoicingMode(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def test_invoicing_mode(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Invoicing Mode",
            }
        )
        self.assertEqual("ten_days", partner.invoicing_mode)
