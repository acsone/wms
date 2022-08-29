# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.delivery_rounds.tests.common import DeliverDeliveryRoundTestCase


class TestExcludePickings(DeliverDeliveryRoundTestCase):
    """Test to run at install
    """

    def test_picking_assign_blocked_by_so(self):
        """
        Data:
            2 SO for :
              the same partner
              the same carrier
              do_not_deliver_if_alone is True
            The carrier is linked to a delivery template without instances
            The SO are confirmed with delivery_step pic + ship
            The outgoing picking is groupbypartner
        Test Case:
            Create a delivery round
            Assign the 2 pickings
        Expected results:
            The pickings are into the round
            The 2 pickings PICK are available
            The 2 SO SHIP are into the same shipping
        """
        sale1 = self._confirm_sale_order(
            carrier_id=self.delivery_carrier.id,
            so_values={"do_not_deliver_if_alone": True},
        )
        sale2 = self._confirm_sale_order(
            carrier_id=self.delivery_carrier.id,
            so_values={"do_not_deliver_if_alone": True},
        )

        # the SO
        sales = self.env["sale.order"].browse([sale1.id, sale2.id])
        self.assertFalse(sales.mapped("picking_ids.delivery_round_id"))

        # check the pickings
        # PICK has picking_type.groupbypartner = False  -> 1 by SO
        picks = sales.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertEqual(len(picks), 2)
        # outgoring has picking_type.groupbypartner = True -> 1 for the 2 SO
        ships = sales.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )
        self.assertEqual(len(ships), 1)

        # create the delivery rounf
        delivery_round = self.env["round.instance"].create(
            {"template_id": self.delivery_template_2.id, "date": "2017-01-01"}
        )

        # now that a delivery round is created for the same template as the one
        # linked to the carrier, the job assign should not link all the pickings to
        # this new delivery since do_not_deliver_if_alone  is set to True
        picks.with_context(round_autoset=True)._job_action_assign()
        self.assertFalse(sales.mapped("picking_ids.delivery_round_id"))
        self.assertListEqual(picks.mapped("state"), ["confirmed", "confirmed"])

        # if one of the picking can be delivered (do_not_deliver_if_alone=False)
        # then the 2 picks are assigned
        sale3 = self._confirm_sale_order(
            carrier_id=self.delivery_carrier.id,
            so_values={"do_not_deliver_if_alone": False},
        )
        sales |= sale3
        picks = sales.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        picks.with_context(round_autoset=True)._job_action_assign()
        self.assertEqual(sales.mapped("picking_ids.delivery_round_id"), delivery_round)
        self.assertListEqual(
            picks.mapped("state"), ["assigned", "assigned", "assigned"]
        )
