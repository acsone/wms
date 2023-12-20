# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command

from .common import TestGetDeviceToUseCommon


class TestGetDeviceToUse(TestGetDeviceToUseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_get_device_to_use_for_specific_customer(self):
        """
        Data: 3 picks of type 1, total of 4 products for a volume of 60m3.

              2 specific devices (3 and 6) are linked to partner.
        Test case: We have 3 devices possibles (device1, device2, device3),
        Expected result: device on partner is used
        """
        partner1_devices = self.device3 | self.device6
        self.partner1.write({"device_type_ids": [Command.set(partner1_devices.ids)]})
        self.assertEqual(self.partner1.device_type_ids, partner1_devices)

        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [Command.link(self.picking_type_1.id)],
                "stock_device_type_ids": [
                    Command.link(self.device1.id),
                    Command.link(self.device2.id),
                    Command.link(self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, self.pick3)
        device = make_picking_batch._compute_device_to_use(first_picking)
        self.assertEqual(device, self.device3)

    def test_no_device_for_the_zone_on_customer(self):
        """
        Data: 3 picks of type 1, total of 4 products for a volume of 60m3.

              2 specific devices (4 and 6) are linked to partner.
        Test case: We have 3 devices possibles (device1, device2, device3),
        Expected result: device on the menu is used
        """
        partner1_devices = self.device4 | self.device6
        self.partner1.write({"device_type_ids": [Command.set(partner1_devices.ids)]})
        self.assertEqual(self.partner1.device_type_ids, partner1_devices)

        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [Command.link(self.picking_type_1.id)],
                "stock_device_type_ids": [
                    Command.link(self.device1.id),
                    Command.link(self.device2.id),
                    Command.link(self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, self.pick3)
        device = make_picking_batch._compute_device_to_use(first_picking)
        self.assertEqual(device, self.device3)

    def test_no_device_on_the_partner(self):
        """
        Data: 3 picks of type 1, total of 4 products for a volume of 60m3.

              No specific device is linked to partner.
        Test case: We have 3 devices possibles (device1, device2, device3),
        Expected result: device on the menu is used
        """
        self.assertEqual(len(self.partner1.device_type_ids), 0)
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [Command.link(self.picking_type_1.id)],
                "stock_device_type_ids": [
                    Command.link(self.device1.id),
                    Command.link(self.device2.id),
                    Command.link(self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, self.pick3)
        device = make_picking_batch._compute_device_to_use(first_picking)
        self.assertEqual(device, self.device3)

    def test_get_device_to_use_for_parent_specific_customer(self):
        """
        Data: 3 picks of type 1, total of 4 products for a volume of 60m3.

              2 specific devices (3 and 6) are linked to parent of partner1.
              No specific device link to partner1
        Test case: We have 3 devices possibles (device1, device2, device3),
        Expected result: device on parent_partner is used
        """
        parent_partner = self._create_partner("Parent partner", "77787812344566")
        self.partner1.parent_id = parent_partner
        partner_devices = self.device3 | self.device6
        parent_partner.write({"device_type_ids": [Command.set(partner_devices.ids)]})
        # check no specific device on partner1
        self.assertEqual(len(self.partner1.device_type_ids), 0)
        # check 2 specific devices on parent_partner
        self.assertEqual(parent_partner.device_type_ids, partner_devices)

        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [Command.link(self.picking_type_1.id)],
                "stock_device_type_ids": [
                    Command.link(self.device1.id),
                    Command.link(self.device2.id),
                    Command.link(self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, self.pick3)
        device = make_picking_batch._compute_device_to_use(first_picking)
        self.assertEqual(device, self.device3)

    def test_2_partners_but_second_one_only_with_specific_device_part_of_menu(self):
        """
        Data: 3 picks of type 1, total of 4 products for a volume of 60m3.

              1 picks of type 1 with a higher priority for partner2/

              2 specific devices (3) are linked to partner1.
              No specific device link to partner2

        Pickings for partner2 are first in the list of pickings.
        Test case: We have 3 devices possibles (device1, device3) on the menu,
        Expected result: device on partner2 is used because of the priority
        and partner1 should not be put in the list of pickings to cluster
        since a specific device exists and is also present into the menu
        """
        self.partner1.write({"device_type_ids": [Command.set(self.device3.ids)]})
        partner2 = self._create_partner("Partner2", "77787812344566")
        pick = self._create_picking_pick_and_assign(
            self.picking_type_1.id, priority="1", partner=partner2
        )
        self.picks.write({"priority": "0"})
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [Command.link(self.picking_type_1.id)],
                "stock_device_type_ids": [
                    Command.link(self.device1.id),
                    Command.link(self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, pick)
        device = make_picking_batch._compute_device_to_use(first_picking)
        self.assertEqual(device, self.device1)
        # No next picking to cluster since the selected device is not in the
        # list of devices for the partner1 and partner1 has specific devices
        # into the menu
        batch = make_picking_batch._create_batch()
        self.assertEqual(batch.picking_ids, pick)

    def test_2_partners_but_second_one_only_with_specific_device_not_part_of_menu(self):
        """
        Data: 3 picks of type 1, total of 4 products for a volume of 60m3.

              1 picks of type 1 with a higher priority for partner2/

              1 specific devices (6) is linked to partner1.
              No specific device link to partner2

        Pickings for partner2 are first in the list of pickings.
        Test case: We have 2 devices possibles (device1, device3) on the menu,
        Expected result: device on partner2 is used because of the priority
        and partner1 should be put in the list of pickings to cluster
        since a specific device exists but is not present into the menu
        """
        self.partner1.write({"device_type_ids": [Command.set(self.device6.ids)]})
        partner2 = self._create_partner("Partner2", "77787812344566")
        pick = self._create_picking_pick_and_assign(
            self.picking_type_1.id, priority="1", partner=partner2
        )
        self.picks.write({"priority": "0"})
        make_picking_batch = self.makePickingBatch.create(
            {
                "user_id": self.env.user.id,
                "picking_type_ids": [Command.link(self.picking_type_1.id)],
                "stock_device_type_ids": [
                    Command.link(self.device1.id),
                    Command.link(self.device3.id),
                ],
            }
        )
        first_picking = make_picking_batch._get_first_picking()
        self.assertEqual(first_picking, pick)
        device = make_picking_batch._compute_device_to_use(first_picking)
        self.assertEqual(device, self.device1)
        # partner1 should be put in the list of pickings to cluster
        batch = make_picking_batch._create_batch()
        self.assertIn(self.partner1, batch.picking_ids.mapped("partner_id"))
