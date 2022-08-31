# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import CommonReceptionPharmacyCase


class TestReceptionPharmacy(CommonReceptionPharmacyCase):
    @classmethod
    def _create_and_prepare_so(cls):
        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "carrier_id": cls.carrier.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product2.name,
                            "product_id": cls.product2.id,
                            "product_uom_qty": 15.0,
                            "product_uom": cls.product2.uom_id.id,
                        },
                    )
                ],
            }
        )
        cls.so1.action_confirm()

        cls.picking = cls.so1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        cls.picking.action_confirm()
        cls.picking.action_assign()
        for pack_op in cls.picking.pack_operation_ids:
            pack_op.qty_done = pack_op.product_qty
        cls.picking.action_done()
        cls.shipping = cls.so1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        cls.shipping.action_confirm()
        cls.shipping.action_assign()
        for pack_op in cls.shipping.pack_operation_ids:
            pack_op.qty_done = pack_op.product_qty
        cls.shipping.delivery_round_id = cls.delivery_round_1.id

    def test_00(self):
        # Create reception pharmcy for the given customer
        # assert that the partner_shipping_id = customer delivery id

        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        pharmacy_line = self.ReceptionPharmacyLine.create(
            {
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "wizard_id": reception.id,
            }
        )

        self.assertEqual(pharmacy_line.partner_shipping_id.id, self.partner.id)

    def test_01(self):
        # Create reception pharmacy for the given customer with an existing picking out
        # Check that the pharmacy line is added to the picking out for the customer

        # create the existing pick out
        self._create_and_prepare_so()
        # before pharmacy reception, one item to be delivered
        self.assertEqual(len(self.shipping.move_lines), 1)

        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        self.ReceptionPharmacyLine.create(
            {
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "wizard_id": reception.id,
            }
        )

        pickings = reception.validate()

        # after pharmacy reception, 2 items to be delivered
        self.assertEqual(len(self.shipping.move_lines), 2)
        self.assertTrue(pickings.mapped("delivery_round_id"))

    def test_is_delivered_by_alcyon(self):
        """
        A customer is delivered by alcyon if it's linked to an itinerary
        """
        self.assertTrue(self.partner.is_delivered_by_alcyon)
        self.itinerary.unlink()
        self.assertFalse(self.partner.is_delivered_by_alcyon)

    def test_no_round_auto_assign_if_alone(self):
        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        self.ReceptionPharmacyLine.create(
            {
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "wizard_id": reception.id,
            }
        )

        pickings = reception.validate()
        self.assertFalse(pickings.mapped("delivery_round_id"))
