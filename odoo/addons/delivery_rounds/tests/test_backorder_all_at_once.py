# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import DeliverDeliveryRoundTestCase


class TestBackorderAllAtOnce(DeliverDeliveryRoundTestCase):
    @classmethod
    def setUpClass(cls):
        super(TestBackorderAllAtOnce, cls).setUpClass()
        cls.so = cls._confirm_sale_order(
            carrier_id=cls.delivery_carrier.id, picking_policy="one"
        )
        cls.picking_pick = cls.so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )
        cls.delivery_round = cls.env["round.instance"].create(
            {"template_id": cls.delivery_template_2.id, "date": "2017-01-01"}
        )

    def test_backorders_on_same_delivery_round(self):
        # now that a delivery round is created for the same template as the one
        # linked to the carrier, the job assign must link all the pickings to
        # this new delivery round AND the 2 PICK pickings must be available
        self.picking_pick.with_context(round_autoset=True)._job_action_assign()

        self.assertEqual(
            self.so.mapped("picking_ids.delivery_round_id"), self.delivery_round
        )
        # Transfer picking partially
        self.picking_pick.action_confirm()
        self.picking_pick.force_assign()
        pack_operation = self.picking_pick.pack_operation_product_ids
        pack_operation.write({"qty_done": 3})
        self.ship = self.so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        backorders = self.picking_pick._create_backorder()
        self.assertEqual(backorders.delivery_round_id, self.delivery_round)
