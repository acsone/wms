# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # create carrier
        product = cls.env["product.product"].create(
            {"name": "Service Test", "type": "service"}
        )
        cls.carrier = cls.env["delivery.carrier"].create(
            {"name": "Test carrier", "product_id": product.id}
        )
        # create partners
        cls.partner_base = cls.env["res.partner"].create(
            {
                "name": "test partner_base",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "test partner",
                "property_delivery_carrier_id": cls.carrier.id,
            }
        )

    def test_order_create(self):
        """
        Data: 1 carrier and 2 partners, 1 with and 1 without that carrier.

        case: - create an SO with the partner base then change the partner to the other
                partner then run onchange_partner_id on so
              - remove the carrier from the partner (not base) and create a new SO.
                create an SO with the partner base then change the partner to the other
                partner then run onchange_partner_id on so
        result: - the SO has the same carrier than the partner
                - the SO has no carrier or a carrier != from the partner
        """
        so_1 = self.env["sale.order"].create({"partner_id": self.partner_base.id})
        self.assertEqual(self.partner.property_delivery_carrier_id, self.carrier)
        so_1.partner_id = self.partner
        so_1.onchange_partner_id()
        self.assertEqual(so_1.carrier_id, self.carrier)

        so_2 = self.env["sale.order"].create({"partner_id": self.partner_base.id})
        self.partner.property_delivery_carrier_id = False
        so_2.partner_id = self.partner
        so_2.onchange_partner_id()
        self.assertNotEqual(so_2.carrier_id, self.carrier)
