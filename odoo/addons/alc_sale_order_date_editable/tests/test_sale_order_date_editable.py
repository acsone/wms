# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestSaleOrderDateEditable(TransactionCase):
    def setUp(self):
        super().setUp()
        self.group_edit_confirmation_date = self.env.ref(
            "alc_sale_order_date_editable.group_sale_order_date_edit"
        )
        product = self.env.ref("product.product_product_4")
        partner = self.env.ref("base.res_partner_1")
        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": partner.id,
                "date_order": "2024-10-10",
                "order_line": [
                    Command.create({"product_id": product.id, "product_uom_qty": 1.0})
                ],
            }
        )

    def test_00(self):
        """Test that a user without the appropriate group can't edit the date order."""
        new_date = "2024-10-15"
        so_form = Form(self.sale_order)
        with self.assertRaises(AssertionError):
            so_form.date_order = new_date

    def test_01(self):
        """Test that a user with the appropriate group can edit the date order."""
        new_date = "2024-10-15"
        self.env.user.write(
            {
                "groups_id": [Command.link(self.group_edit_confirmation_date.id)],
            }
        )
        so_form = Form(self.sale_order)
        so_form.date_order = new_date
