# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo.tests import TransactionCase


class TestOrder(TransactionCase):
    @freeze_time("2023-09-01 20:00:00")
    def test_order(self):
        partner = self.env["res.partner"].create({"name": "Partner"})
        sale = self.env["sale.order"].create({"partner_id": partner.id})
        self.assertEqual("2023-09-01", str(sale.date_order_short))
