# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command

from odoo.addons.rma.tests.test_rma import TestRma


class TestStockPickingRmaFields(TestRma):
    def test_origin_rma_update(self):
        """Test that the ram related field of a stock picking gets updated when the original rma gets updated."""
        rma_reason = self.env["rma.reason"].create(
            {
                "name": "Test",
                "description": "test",
                "company_id": self.company.id,
                "allowed_operation_ids": [Command.link(self.operation.id)],
            }
        )
        rma_reason_2 = self.env["rma.reason"].create(
            {
                "name": "Test2",
                "description": "test2",
                "company_id": self.company.id,
                "allowed_operation_ids": [Command.link(self.operation.id)],
            }
        )

        operation = self.env.ref("rma.rma_operation_replace")
        operation_2 = self.env.ref("rma.rma_operation_return")

        rma = self._create_rma(
            self.partner, self.product, 10, self.rma_loc, operation=operation
        )
        rma.reason_id = rma_reason
        rma.action_confirm()
        reception = rma.reception_move_id.picking_id

        self.assertEqual(reception.rma_id.reason_id.name, "Test")
        self.assertEqual(reception.rma_id.operation_id.name, "Replace")

        rma.reason_id = rma_reason_2
        rma.operation_id = operation_2
        self.assertEqual(reception.rma_id.reason_id.name, "Test2")
        self.assertEqual(reception.rma_id.operation_id.name, "Repair")
