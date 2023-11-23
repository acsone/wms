# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestEshopProductDomain(TransactionCase):
    def test_0(self):
        partner = self.env["res.partner"].create(
            {"name": "partner", "partner_type": "veterinary"}
        )
        domain = partner._get_product_domain()
        self.assertEqual(
            domain,
            [
                "&",
                ("allowed_partner_types", "like", "%%veterinary%%"),
                ("web_published", "=", True),
            ],
        )
