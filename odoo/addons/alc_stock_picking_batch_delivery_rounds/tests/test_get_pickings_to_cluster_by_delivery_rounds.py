# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import ClusterPickingDeliveryCommonFeatures


class TestGetPickingsToClusterByDeliveryRounds(ClusterPickingDeliveryCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(TestGetPickingsToClusterByDeliveryRounds, cls).setUpClass()

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.stock_location.write(
            {"zone": "G", "corridor": "A", "shelf": "42", "height": "4", "box": "B12"}
        )
        cls.delivery_round2.picking_launched = True
        cls.delivery_round1.picking_launched = True

    def test_get_pickings_by_delivery_rounds_operator_allowed_on_both_delivery_rounds(
        self,
    ):
        """
        Data: 2 delivery rounds, both ok for operator 1
        Test case: we ask for a cluster for operator 1
        Expected result: Pickings to be retrieved are the ones related to delivery 2
        """
        self.operator_1.only_one_delivery_round_by_cluster = True
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.operator_1.id,
                "picking_type_ids": [(4, self.picking_type_ali.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
            }
        )
        candidates_pickings = make_picking_batch._candidates_pickings_to_batch(
            user=self.operator_1
        )
        picks_ali = self.pick4 | self.pick5
        self.assertEqual(candidates_pickings, picks_ali)

    def test_get_pickings_by_delivery_rounds_operator_allowed_only_on_delivery_1(self):
        """
        Data: 2 delivery rounds. Delivery 2 is only for operator 1
        Test case: we ask for a cluster for operator 2
        Expected result: Pickings to be retrieved are the ones related to delivery 1
        """
        self.operator_1.only_one_delivery_round_by_cluster = True
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.operator_2.id,
                "picking_type_ids": [(4, self.picking_type_ali.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
            }
        )
        candidates_pickings = make_picking_batch._candidates_pickings_to_batch(
            user=self.operator_1
        )
        picks_ali = self.pick6
        self.assertEqual(candidates_pickings, picks_ali)

    def test_can_mix_delivery_rounds(self):
        self.operator_1.only_one_delivery_round_by_cluster = False

        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.operator_1.id,
                "picking_type_ids": [(4, self.picking_type_ali.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
                "only_one_delivery_round_by_cluster": False,
            }
        )
        candidates_pickings = make_picking_batch._candidates_pickings_to_batch(
            user=self.operator_1
        )
        # picks 4 and 5 and in deliveryround 2, pick6 is in deliveryround 1
        picks_ali = self.pick4 | self.pick5 | self.pick6
        self.assertEqual(candidates_pickings, picks_ali)

    def test_cannot_mix_delivery_rounds_on_menu(self):
        self.operator_1.only_one_delivery_round_by_cluster = False

        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.operator_1.id,
                "picking_type_ids": [(4, self.picking_type_ali.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
                "only_one_delivery_round_by_cluster": True,
            }
        )
        candidates_pickings = make_picking_batch._candidates_pickings_to_batch(
            user=self.operator_1
        )
        # picks 4 and 5 and in deliveryround
        picks_ali = self.pick4 | self.pick5
        self.assertEqual(candidates_pickings, picks_ali)

    def test_cannot_mix_delivery_rounds_on_user(self):
        self.operator_1.only_one_delivery_round_by_cluster = True

        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.operator_1.id,
                "picking_type_ids": [(4, self.picking_type_ali.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
                "only_one_delivery_round_by_cluster": False,
            }
        )
        candidates_pickings = make_picking_batch._candidates_pickings_to_batch(
            user=self.operator_1
        )
        # picks 4 and 5 and in deliveryround
        picks_ali = self.pick4 | self.pick5
        self.assertEqual(candidates_pickings, picks_ali)
