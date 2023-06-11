# Copyright 2020 Camptocamp (https://www.camptocamp.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from .common import ReleaseChannelCase


class TestReleaseChannelPartner(ReleaseChannelCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "partner"})
        cls.partner_channel = cls._create_channel(
            name="Partner channel",
            sequence=1,
            code="pickings = pickings.filtered(lambda p: p.priority == 'x')",
        )
        cls.other_channel = cls._create_channel(
            name="Test Domain",
            sequence=1,
            rule_domain=[("priority", "=", "1")],
        )
        cls.move = cls._create_single_move(cls.product1, 10)
        cls.move2 = cls._create_single_move(cls.product2, 10)
        cls.move.picking_id.priority = "1"
        cls.move.picking_id.partner_id = partner
        partner2 = cls.env["res.partner"].create({"name": "partner"})
        cls.move2.picking_id.priority = "1"
        cls.move2.picking_id.partner_id = partner2
        partner2.stock_release_channel_id = False
        cls.moves = cls.move + cls.move2

    def test_00(self):
        """the picking must be assigned to partner channel despite it fit or not other
        channels criteria"""
        self.moves.picking_id.assign_release_channel()
        self.assertEqual(self.move.picking_id.release_channel_id, self.partner_channel)
        self.assertEqual(self.move2.picking_id.release_channel_id, self.other_channel)

    def test_01(self):
        """partner channel is not assigned if isn't active"""
        self.partner_channel.active = False
        self.moves.picking_id.assign_release_channel()
        self.assertEqual(self.move.picking_id.release_channel_id, self.other_channel)
        self.assertEqual(self.move2.picking_id.release_channel_id, self.other_channel)

    def test_02(self):
        """partner channel is not assigned if it's asleep"""
        self.partner_channel.state = "asleep"
        self.moves.picking_id.assign_release_channel()
        self.assertEqual(self.move.picking_id.release_channel_id, self.other_channel)
        self.assertEqual(self.move2.picking_id.release_channel_id, self.other_channel)
