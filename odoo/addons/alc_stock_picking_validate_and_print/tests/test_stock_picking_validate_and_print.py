# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestStockPickingValidateAndPrint(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, discard_logo_check=True))
        cls.assigned_deliveries = cls.env["stock.picking"].search(
            [("state", "=", "assigned"), ("picking_type_code", "=", "outgoing")]
        )
        cls.not_assigned_deliveries = cls.env["stock.picking"].search(
            [("state", "!=", "assigned"), ("picking_type_code", "=", "outgoing")]
        )
        cls.assigned_not_deliveries = cls.env["stock.picking"].search(
            [("state", "!=", "assigned"), ("picking_type_code", "!=", "outgoing")]
        )

    def test_0(self):
        with self.assertRaises(UserError):
            self.not_assigned_deliveries.action_validate_and_print_delivery()
        with self.assertRaises(UserError):
            self.assigned_not_deliveries.action_validate_and_print_delivery()
        res = self.assigned_deliveries.action_validate_and_print_delivery()
        self.assertEqual(res.get("type"), "ir.actions.report")
        self.assertEqual(res.get("report_name"), "stock.report_deliveryslip")
        self.assertEqual(res.get("report_type"), "qweb-pdf")
