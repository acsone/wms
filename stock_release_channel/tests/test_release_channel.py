# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import exceptions

from .common import ReleaseChannelCase


class TestReleaseChannel(ReleaseChannelCase):
    def _test_assign_channels(self, expected):
        move = self._create_single_move(self.product1, 10)
        move.picking_id.priority = "1"
        move2 = self._create_single_move(self.product2, 10)
        (move + move2).picking_id.assign_release_channel()
        self.assertEqual(move.picking_id.release_channel_id, expected)
        self.assertEqual(move2.picking_id.release_channel_id, self.default_channel)

    def test_assign_channel_domain(self):
        channel = self._create_channel(
            name="Test Domain",
            sequence=1,
            rule_domain=[("priority", "=", "1")],
        )
        self._test_assign_channels(channel)

    def test_assign_channel_code(self):
        channel = self._create_channel(
            name="Test Code",
            sequence=1,
            code="pickings = pickings.filtered(lambda p: p.priority == '1')",
        )
        self._test_assign_channels(channel)

    def test_assign_partner_channel(self):
        """the picking must be assigned to partner channel despite it fit or not other
        channels criteria"""
        partner = self.env["res.partner"].create({"name": "partner"})
        partner_channel = self._create_channel(
            name="Partner channel",
            sequence=1,
            code="pickings = pickings.filtered(lambda p: p.priority == 'x')",
        )
        other_channel = self._create_channel(
            name="Test Domain",
            sequence=1,
            rule_domain=[("priority", "=", "1")],
        )
        move = self._create_single_move(self.product1, 10)
        move.picking_id.priority = "1"
        move.picking_id.partner_id = partner
        partner.stock_release_channel_id = partner_channel

        partner2 = self.env["res.partner"].create({"name": "partner"})
        move2 = self._create_single_move(self.product2, 10)
        move2.picking_id.priority = "1"
        move2.picking_id.partner_id = partner2
        partner2.stock_release_channel_id = False

        (move + move2).picking_id.assign_release_channel()
        self.assertEqual(move.picking_id.release_channel_id, partner_channel)
        self.assertEqual(move2.picking_id.release_channel_id, other_channel)

    def test_assign_channel_domain_and_code(self):
        channel = self._create_channel(
            name="Test Code",
            sequence=1,
            rule_domain=[("priority", "=", "1")],
            code="pickings = pickings.filtered(lambda p: p.priority == '1')",
        )
        self._test_assign_channels(channel)

    def test_invalid_code(self):
        with self.assertRaises(exceptions.ValidationError):
            self._create_channel(
                name="Test Code",
                sequence=1,
                code="pickings = pickings.filtered(",
            )

    def test_default_sequence(self):
        channel = self._create_channel(name="Test1")
        self.assertEqual(channel.sequence, 0)
        channel2 = self._create_channel(name="Test2")
        self.assertEqual(channel2.sequence, 10)
        channel3 = self._create_channel(name="Test3")
        self.assertEqual(channel3.sequence, 20)
