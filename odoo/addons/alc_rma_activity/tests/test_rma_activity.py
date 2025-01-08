# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.rma.tests.test_rma import TestRma


class TestRmaActivity(TestRma):
    def test_00(self):
        self.operation.create_inventory_activity = True
        rma = self._create_rma(self.partner, self.product, 10, self.rma_loc)
        rma.action_confirm()
        activity = self.env["mail.activity"].search(
            [
                ("res_model_id", "=", self.env["ir.model"]._get("rma").id),
                ("res_id", "=", rma.id),
                ("summary", "=", "Inventory actions required"),
            ]
        )
        self.assertEqual(len(activity), 1, "Activity was not created after reception.")
