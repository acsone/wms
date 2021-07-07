# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.delivery_rounds.tests.test_deliveryround_assign_2 import (
    DeliveryRoundAssignTestCase,
)


class TestRoundInstance(DeliveryRoundAssignTestCase):
    """Test to run at install
    """

    def test_all_at_once_no_assignable_00(self):
        """
        In this test we check that if one a the pick pickings created from a SO
        with an "all at once" picking policy is not available, non of the pickings
        are put into an existing delivery round if a delivery round exists when
        the so is confirmed
        """
        # add p1 qty into medoc and link to route medoc
        self._set_qty_in_loc_only(self.p1, 10, self.location_product_medoc)
        self.p1.categ_id = self.categ_medoc
        self.p1.route_ids = [(6, 0, self.route_medoc.ids)]
        # link p2 to route alime (no qty)
        self.p2.categ_id = self.categ_ali
        self.p2.route_ids = [(6, 0, self.route_aliment.ids)]

        # create delivery round so the SO could be assigned to this delivery round
        delivery_round = self.env["round.instance"].create(
            {"template_id": self.delivery_template_2.id, "date": "2017-01-01"}
        )
        delivery_round.button_resetdraft()
        sale = self._confirm_sale_order(
            partner=self.partner1,
            carrier_id=self.delivery_carrier.id,
            product=self.p1 | self.p2,
            picking_policy="one",
        )
        self.assertFalse(sale.mapped("picking_ids.delivery_round_id"))

        # if both products are available the pickings are assigned to the delivery round
        self._set_qty_in_loc_only(self.p2, 10, self.location_product_alim)
        self.assertFalse(sale.mapped("picking_ids.delivery_round_id"))
        sale2 = self._confirm_sale_order(
            partner=self.partner1,
            carrier_id=self.delivery_carrier.id,
            product=self.p1 | self.p2,
            picking_policy="one",
        )
        self.assertEqual(sale2.mapped("picking_ids.delivery_round_id"), delivery_round)
