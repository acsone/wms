# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma.tests.test_rma import TestRma


class TestDuplicateDeliverySlip(TestRma):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product.id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "inventory_quantity": 20,
            }
        )._apply_inventory()

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

    def test_1(self):
        """Check that rma reception are printed before delivery."""
        self.operation.action_create_delivery = "automatic_on_confirm"
        rma = self._create_rma(self.partner, self.product, 10, self.rma_loc)
        rma.action_confirm()
        reception = rma.reception_move_id.picking_id
        delivery = rma.delivery_move_ids.picking_id
        reception.picking_type_id.is_rma = True
        sa = self.env["shipment.advice"].create({"shipment_type": "outgoing"})
        reception.rma_shipment_advice_id = sa
        delivery.move_line_ids.shipment_advice_id = sa
        self.assertEqual(sa.rma_picking_ids, reception)
        self.assertEqual(sa.loaded_picking_ids, delivery)
        action = sa.with_context(discard_logo_check=True).print_all_deliveryslip()
        active_ids = action.get("context", {}).get("active_ids", [])
        self.assertEqual(active_ids, [reception.id, delivery.id])

        rma2 = self._create_rma(self.partner, self.product, 10, self.rma_loc)
        rma2.action_confirm()
        reception2 = rma2.reception_move_id.picking_id
        delivery2 = rma2.delivery_move_ids.picking_id
        reception2.rma_shipment_advice_id = sa
        delivery2.move_line_ids.shipment_advice_id = sa
        reception2.toursolver_shipment_advice_rank = 10
        delivery2.toursolver_shipment_advice_rank = 10
        action = sa.with_context(discard_logo_check=True).print_all_deliveryslip()
        active_ids = action.get("context", {}).get("active_ids", [])
        self.assertListEqual(
            active_ids, [reception.id, delivery.id, reception2.id, delivery2.id]
        )
