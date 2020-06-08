# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import GroupByPartnerCommonCase


class TestProcurementGroup(GroupByPartnerCommonCase):
    def test_00(self):
        """
        Data:
            2 partners
        Test Case:
            Create and confirm a SO with a shipping address <> du SO partner
            and a fixed carrrier
            * partner1 as partner
            * partner2 as partner_shipping_id
            * carrier_fixed as carrier
        Expected result:
            Into the new procurement group:
                partner1 is saved as customer_id
                partner2 is saved as partner_id
                carrier_fixed is saved as carrier_id
        """

    def test_propagate_carrier_to_group(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "partner_shipping_id": self.partner2.id,
                "carrier_id": self.carrier_fixed.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": self.p1.name,
                            "product_id": self.p1.id,
                            "product_uom": self.ref("product.product_uom_unit"),
                            "product_uom_qty": 3,
                            "price_unit": 200,
                        },
                    )
                ],
            }
        )
        sale.action_confirm()
        pg = sale.procurement_group_id
        self.assertEqual(sale.partner_id, pg.customer_id)
        self.assertEqual(sale.partner_shipping_id, pg.partner_id)
        self.assertEqual(sale.carrier_id, pg.carrier_id)
