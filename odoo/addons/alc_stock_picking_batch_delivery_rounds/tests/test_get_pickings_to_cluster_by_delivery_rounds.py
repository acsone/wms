# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import ClusterPickingDeliveryCommonFeatures


class TestGetPickingsToClusterByDeliveryRounds(ClusterPickingDeliveryCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(TestGetPickingsToClusterByDeliveryRounds, cls).setUpClass()
        picks_ali = cls.env["stock.picking"].search(
            [
                ("picking_type_subcode", "=", "PICK"),
                ("picking_type_id", "=", cls.picking_type_ali.id),
            ]
        )
        for pick in picks_ali:
            pick.force_assign()

        picks_ali[0].write({"priority": "3", "rank": 300})
        picks_ali[1].write({"priority": "3", "rank": 700})
        picks_ali[2].write({"priority": "1", "rank": 1300})

        pickings2 = cls.pick4 | cls.pick5
        cls.delivery_round2._assign_pickings(pickings2)

    def test_get_pickings_by_delivery_rounds_operator_allowed_on_both_delivery_rounds(
        self,
    ):
        """
        Data: 2 delivery rounds, both ok for operator 1
        Test case: we ask for a cluster for operator 1
        Expected result: Pickings to be retrieved are the ones related to delivery 2
        """
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.operator_1.id,
                "picking_type_ids": [(4, self.picking_type_ali.id)],
                "stock_device_type_line_ids": [
                    (4, self.device_line1.id),
                    (4, self.device_line2.id),
                    (4, self.device_line3.id),
                ],
            }
        )
        candidates_pickings = make_picking_batch._search_pickings()
        picks_ali = self.pick4 | self.pick5
        self.assertEqual(candidates_pickings, picks_ali)

    def test_get_pickings_by_delivery_rounds_operator_allowed_only_on_delivery_1(self):
        """
        Data: 2 delivery rounds. Delivery 2 is only for operator 1
        Test case: we ask for a cluster for operator 2
        Expected result: Pickings to be retrieved are the ones related to delivery 1
        """
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.operator_2.id,
                "picking_type_ids": [(4, self.picking_type_ali.id)],
                "stock_device_type_line_ids": [
                    (4, self.device_line1.id),
                    (4, self.device_line2.id),
                    (4, self.device_line3.id),
                ],
            }
        )
        candidates_pickings = make_picking_batch._search_pickings()
        picks_ali = self.pick6
        self.assertEqual(candidates_pickings, picks_ali)
