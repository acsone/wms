# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestReceptionPharmacy(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestReceptionPharmacy, cls).setUpClass()

        # Create customer with delivery address
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "street": "25 rue des bourgeois",
                "zip": "5000",
                "country_id": cls.env.ref("base.be").id,
                "type": "delivery",
            }
        )

        # Create the product for reception
        cls.product = cls.env["product.template"].browse(
            cls.env.ref("specific_stock.product_colis_souverain").id
        )

        cls.bin = cls.env["stock.location"].create({"name": "Test unit"})

        # Instance of reception pharmacy
        cls.ReceptionPharmacy = cls.env["reception.pharmacy"]
        cls.ReceptionPharmacyLine = cls.env["reception.pharmacy.line"]

        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "TST",
            }
        )
        cls.warehouse_1.pick_type_id.subcode = "PICK"

        cls.warehouse_1.pick_type_id.groupbypartner = True
        cls.warehouse_1.out_type_id.groupbypartner = True
        cls.delivery_template = cls.env["round.template"].create(
            {"name": "Unittest delivery template"}
        )
        cls.carrier = cls.env["delivery.carrier"].search(
            [("free_if_more_than", "=", False)], limit=1
        )

        cls.delivery_round_1 = cls.env["round.instance"].create(
            {"template_id": cls.delivery_template.id, "date": "2020-11-18"}
        )
        cls.carrier.delivery_template_id = cls.delivery_template.id

        cls.env["ir.model.data"].create(
            {
                "module": "__setup__",
                "name": "deliver_carrier_alcyon",
                "model": "delivery.carrier",
                "res_id": cls.carrier.id,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "test product2",
                "default_code": "987654312",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.itinerary = cls.env["round.itinerary"].create(
            {
                "name": "Itinerary test",
                "code": "T17C",
                "sequence": 22,
                "partner_position_ids": [
                    (0, 0, {"sequence": 10, "partner_id": cls.partner.id})
                ],
            }
        )
        cls.delivery_round_1.itinerary_ids = cls.itinerary
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
        reception.validate()

        # after pharmacy reception, 2 items to be delivered
        self.assertEqual(len(self.shipping.move_lines), 2)
