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

        # create the delivery round
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

    def test_assign_non_blocking_picking_assign_blocked_picking(self):
        """Test that the assignation of a new picking will also assign pickings
        previously blocked
        """
        # assign blocked picking -> not assigned
        blocked_pick, blocked_ship = self._create_picking_pick_ship(
            partner=self.partner2
        )
        blocked_pick.move_lines.delivery_requires_other_lines = True
        # we do not take care of reservation but put the picking into
        # the rigth state to be available...
        blocked_pick.move_lines.write({"state": "assigned"})
        self.delivery_round_1._assign_pickings(blocked_pick)
        self.assertFalse(blocked_pick.delivery_round_id)

        # assign normal picking for the same partner
        # -> both pickings are assigned
        pick = self._create_picking_pick(partner=self.partner2)
        self._add_picking_pick_to_picking_out(pick, blocked_ship)
        pick.move_lines.write({"state": "assigned"})
        self.delivery_round_1._assign_pickings(pick)
        self.assertTrue(pick.delivery_round_id)
        self.assertTrue(blocked_pick.delivery_round_id)

    def test_ignore_delivery_round_assign_block(self):
        blocked_pick, blocked_ship = self._create_picking_pick_ship(
            partner=self.partner2
        )
        blocked_pick.move_lines.delivery_requires_other_lines = True
        # we do not take care of reservation but put the picking into
        # the rigth state to be available...
        blocked_pick.move_lines.write({"state": "assigned"})
        blocked_ship.move_lines.write({"state": "assigned"})
        self.delivery_round_1._assign_pickings(blocked_pick)
        self.assertFalse(blocked_pick.delivery_round_id)
        self.assertFalse(blocked_ship.delivery_round_id)
        blocked_pick.ignore_delivery_round_assign_block = True
        self.delivery_round_1._assign_pickings(blocked_pick)
        self.assertTrue(blocked_pick.delivery_round_id)
        self.assertTrue(blocked_ship.delivery_round_id)

    def test_assign_on_so_confirm(self):
        """In this test we check that a blocked picking is not assigned at
        conformation to a delivery round if blocked and no other pickings for
        the same partner are already part of the delivery. We also check that
        if a new SO is confirmed, the 2 pickings are assigned to the delivery"""

        # we create the delivery round for the same template as the one linked
        # to the carrier
        self.env["round.instance"].create(
            {"template_id": self.delivery_template_2.id, "date": "2017-01-01"}
        )
        sale1 = self._confirm_sale_order(
            carrier_id=self.delivery_carrier.id,
            so_values={"do_not_deliver_if_alone": True},
        )
        # at this stage, even if the pick is available and a delivery exists
        # the pick is not part of the delivery since it's alone...
        pick1 = sale1.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertFalse(pick1.delivery_round_id)

        # we create a new order for the same partner
        sale2 = self._confirm_sale_order(carrier_id=self.delivery_carrier.id)
        pick2 = sale2.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertTrue(pick2.delivery_round_id)
        self.assertTrue(pick1.delivery_round_id)

        # if we create a new 'blocked' picking now, it will be assigned to
        # the delivery since we already have pickings for the same partner into
        # the delivery
        sale3 = self._confirm_sale_order(
            carrier_id=self.delivery_carrier.id,
            so_values={"do_not_deliver_if_alone": True},
        )
        pick3 = sale3.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        self.assertTrue(pick3.delivery_round_id)

        # this test is only valide if PICK has picking_type.groupbypartner
        # = False  -> 1 by SO
        self.assertNotEqual(pick3, pick2)
