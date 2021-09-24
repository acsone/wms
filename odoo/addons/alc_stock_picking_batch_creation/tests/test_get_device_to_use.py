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
        Data: one pick for a user that need to be delivered on a specific device
        Test case: We check the device for this user, even though the "device3" should be selected
        according to the volume, since its a specific user, it will not be the case
        Expected result: palette is selected
        """
        self.partner_category = self.env.ref(
            "alc_stock_picking_batch_creation.res_partner_category_deliver_pal"
        )
        self.partner1.write({"category_id": [(4, self.partner_category.id, 0)]})

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
        palette = self.env.ref("alc_stock_picking_batch_creation.palette")
        candidates_pickings = make_picking_batch._search_pickings()
        for picking in candidates_pickings:
            device = make_picking_batch._compute_device_to_use(picking)
            if device:
                break
        self.assertEqual(device, palette)
