# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockPickingCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.user_1 = cls.env.ref("base.user_demo")
        cls.user_2 = cls.user_1.copy({"name": "demo user 2"})
        cls.allowed_users = cls.user_2 | cls.user_1
        cls.not_allowed_user = cls.user_2.copy({"name": "demo user 3"})
        cls.release_channel = cls.env["stock.release.channel"].create(
            {"name": "release channel"}
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "location_dest_id": cls.env.ref("stock.stock_location_stock").id,
                "release_channel_id": cls.release_channel.id,
            }
        )

    def setUp(self):
        super().setUp()
        self.release_channel.user_ids = self.allowed_users
