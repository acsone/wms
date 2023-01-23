# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import AlcClusterPickingCommonFeatures


class TestGetDeviceToUse(AlcClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(TestGetDeviceToUse, cls).setUpClass()

    def test_get_device_to_use_for_specific_customer(self):
        """
        Expected result: device on user is used
        """
        partner1_devices = self.device3 | self.device6
        self.partner1.write({"device_type_ids": [(6, 0, partner1_devices.ids)]})

        self._create_picking_pick_and_assign(
            self.picking_type_ali.id, products=self.p2 | self.p4
        )
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_ali.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
            }
        )
        candidates_pickings = make_picking_batch._search_pickings()
        for picking in candidates_pickings:
            device = make_picking_batch._compute_device_to_use(picking)
            if device:
                break
        self.assertEqual(device, self.device3)

    def test_no_device_for_the_zone_on_customer(self):
        """
        Expected result: device on the menu is used
        """
        partner1_devices = self.device4 | self.device6
        self.partner1.write({"device_type_ids": [(6, 0, partner1_devices.ids)]})

        self._create_picking_pick_and_assign(
            self.picking_type_ali.id, products=self.p2 | self.p4
        )
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_ali.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
            }
        )
        candidates_pickings = make_picking_batch._search_pickings()
        for picking in candidates_pickings:
            device = make_picking_batch._compute_device_to_use(picking)
            if device:
                break
        self.assertEqual(device, self.device3)

    def test_no_device_on_the_partner(self):
        """
        Expected result: device on the menu is used
        """
        self._create_picking_pick_and_assign(
            self.picking_type_ali.id, products=self.p2 | self.p4
        )
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_ali.id)],
                "stock_device_type_ids": [
                    (4, self.device1.id),
                    (4, self.device2.id),
                    (4, self.device3.id),
                ],
            }
        )
        candidates_pickings = make_picking_batch._search_pickings()
        for picking in candidates_pickings:
            device = make_picking_batch._compute_device_to_use(picking)
            if device:
                break
        self.assertEqual(device, self.device3)

    def test_check_volume_picking_computed(self):
        partner1_devices = self.device3
        self.partner1.write({"device_type_ids": [(6, 0, partner1_devices.ids)]})

        self._create_picking_pick_and_assign(
            self.picking_type_ali.id, products=self.p2 | self.p4
        )
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [(4, self.picking_type_ali.id)],
                "stock_device_type_ids": [(4, self.device1.id)],
            }
        )
        candidates_pickings = make_picking_batch._search_pickings()
        volume_pickings = candidates_pickings.mapped("total_volume_batch_picking")
        for volume in volume_pickings:
            self.assertEqual(volume, 0)
        for picking in candidates_pickings:
            device = make_picking_batch._compute_device_to_use(picking)
            if device:
                break
        volume_pickings = candidates_pickings.mapped("total_volume_batch_picking")
        for volume in volume_pickings:
            self.assertEqual(volume, 60)
