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
