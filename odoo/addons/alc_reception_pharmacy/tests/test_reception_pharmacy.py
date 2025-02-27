# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.exceptions import UserError

from .common import CommonReceptionPharmacyCase


class TestReceptionPharmacy(CommonReceptionPharmacyCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env.user.company_id.delivered_by_alcyon_constraint = False
        cls.wizard = cls.env["receive.pharmacy.products"]
        cls.bin2 = cls.env["stock.location"].create({"name": "Test unit 2"})

    def test_00(self):
        # Create reception pharmacy for the given customer
        # assert that the partner_shipping_id = customer delivery id

        # create the existing pick out
        self._create_and_prepare_so()
        # before pharmacy reception, one item to be delivered
        self.assertEqual(len(self.shipping.move_line_ids), 1)

        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "lot_name": "TC54636",
                "product_qty": 1,
            }
        )
        wiz.validate_reception()
        pharmacy_line = self.env["reception.pharmacy.line"].search(
            [("wizard_id", "=", reception.id)]
        )
        self.assertEqual(pharmacy_line.partner_shipping_id.id, self.partner.id)

        self._validate_reception_and_return_picking(reception)

        # after pharmacy reception, 2 items to be delivered
        self.assertEqual(len(self.shipping.move_ids), 2)

    def test_01(self):
        # Create reception pharmacy for the given customer with an existing picking out
        # Check that the pharmacy line is added to the picking out for the customer

        # create the existing pick out
        self._create_and_prepare_so()
        # before pharmacy reception, one item to be delivered
        self.assertEqual(len(self.shipping.move_line_ids), 1)

        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "lot_name": "TC546736",
                "product_qty": 1,
            }
        )
        wiz.validate_reception()

        self._validate_reception_and_return_picking(reception)
        # after pharmacy reception, 2 items to be delivered
        self.assertEqual(len(self.shipping.move_ids), 2)

    def test_new_shipping_if_alone(self):
        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "lot_name": "TC512344636",
                "product_qty": 1,
            }
        )
        wiz.validate_reception()
        pharmacy_line = self.env["reception.pharmacy.line"].search(
            [("wizard_id", "=", reception.id)]
        )

        pickings = self._validate_reception_and_return_picking(reception)
        self.assertTrue(pickings)
        move = pickings.move_ids
        self.assertEqual(move.product_id, reception.product_id)
        self.assertEqual(move.restrict_lot_id, pharmacy_line.lot_id)

    def test_several_reception_for_one_customer(self):
        """
        2 receptions for the same client lead to 2 different shippings because carrier.

        is not automatically set
        """
        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "lot_name": "TC123467436",
                "product_qty": 1,
            }
        )
        wiz.validate_reception()

        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin2.id,
                "lot_name": "TC90876",
                "product_qty": 1,
            }
        )
        wiz.validate_reception()

        pharmacy_lines = self.env["reception.pharmacy.line"].search(
            [("wizard_id", "=", reception.id)]
        )
        self.assertEqual(len(pharmacy_lines), 2)
        self.assertEqual(pharmacy_lines.mapped("customer_id"), self.partner)
        pickings = self._validate_reception_and_return_picking(reception)
        shippings = pickings.filtered(lambda p: p.picking_type_id.code == "outgoing")

        self.assertEqual(len(shippings), 1)  # same carrier, pickings are merged
        self.assertEqual(reception.state, "done")
        self.assertEqual(reception.line_ids.mapped("state"), ["done", "done"])

    @freeze_time("2023-01-01 00:00:00")
    def test_lot_name(self):
        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "lot_name": "TC12345",
                "product_qty": 1,
            }
        )
        wiz.validate_reception()

        pharmacy_line = self.env["reception.pharmacy.line"].search(
            [("wizard_id", "=", reception.id)]
        )
        lot = pharmacy_line.lot_id

        self.assertEqual(lot.name, "2023TC12345")

    def test_action_cancel(self):
        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "lot_name": "TC123467436",
                "product_qty": 1,
            }
        )
        wiz.validate_reception()
        reception.action_cancel()
        self.assertEqual(reception.line_ids.state, "cancel")
        self.assertEqual(reception.state, "cancel")

    def test_action_cancel_not_allowed(self):
        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        wiz = self.wizard.create(
            {
                "reception_pharmacy_id": reception.id,
                "customer_id": self.partner.id,
                "bin_id": self.bin.id,
                "lot_name": "TC123467436",
                "product_qty": 1,
            }
        )
        wiz.validate_reception()
        self._validate_reception_and_return_picking(reception)
        with self.assertRaises(UserError):
            reception.action_cancel()

    def test_action_cancel_no_line(self):
        reception = self.ReceptionPharmacy.create({"product_id": self.product.id})
        reception.action_cancel()
        self.assertEqual(reception.state, "cancel")
