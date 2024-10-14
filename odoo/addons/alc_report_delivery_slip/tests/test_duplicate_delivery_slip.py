# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma.tests.test_rma import TestRma


class TestDuplicateDeliverySlip(TestRma):
    def test_0(self):
        """
        Operation.duplicate_delivery_slip_at_reception = to False.

            neither the reception nor delivery pickings have a duplicate slip
        operation.duplicate_delivery_slip_at_reception = True
            only the reception have a duplicate slip
        """
        self.operation.duplicate_delivery_slip_at_reception = False
        self.operation.action_create_delivery = "automatic_on_confirm"
        rma = self._create_rma(self.partner, self.product, 10, self.rma_loc)
        rma.action_confirm()
        reception = rma.reception_move_id.picking_id
        delivery = rma.delivery_move_ids.picking_id
        self.assertTrue(rma.reception_move_id.picking_id)
        self.assertTrue(delivery)
        self.assertFalse(reception.duplicate_delivery_slip)
        self.assertFalse(delivery.duplicate_delivery_slip)
        self.operation.duplicate_delivery_slip_at_reception = True
        self.assertTrue(reception.duplicate_delivery_slip)
        self.assertFalse(delivery.duplicate_delivery_slip)
