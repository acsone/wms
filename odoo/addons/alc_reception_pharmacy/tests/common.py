# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class CommonReceptionPharmacyCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(CommonReceptionPharmacyCase, cls).setUpClass()

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
            cls.env.ref("alc_reception_pharmacy.product_colis_souverain").id
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
                "barcode": "YYY0007",
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
