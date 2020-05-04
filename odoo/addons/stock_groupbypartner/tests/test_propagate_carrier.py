# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import GroupByPartnerCommonCase


class TestPropagateCarrier(GroupByPartnerCommonCase):
    def test_propagate_carrier_to_group(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
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
        self.assertEqual(sale.carrier_id, sale.procurement_group_id.carrier_id)
