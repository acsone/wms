# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestStockPicking(TransactionCase):
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
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "location_dest_id": cls.env.ref("stock.stock_location_stock").id,
                "release_channel_id": cls.release_channel.id,
            }
        )

    def setUp(self):
        super().setUp()
        self.release_channel.user_ids = self.allowed_users

    def test_00(self):
        """
        DATA:

            A round instance with 2 users
            A picking without user
        Test case:
            1. Assign an user part of the list of round instance users
            2. Assign on user not in the list of round instance users
        Expected result:
            1. user is assigned to the picking
            2. ValidationError is raised
        """
        self.picking.user_id = self.user_1
        self.assertEqual(self.picking.user_id, self.user_1)
        with self.assertRaises(ValidationError):
            self.picking.user_id = self.not_allowed_user

    def test_01(self):
        """
        DATA:

            A round instance with 2 users
            A picking with 1 allowed user
        Test case:
            Remove the user linked to the picking from the list of
            users on the round instance
        Expected result:
            No error is raised ans the user is still assigned to the
            picking
        """
        self.picking.user_id = self.user_1
        self.release_channel.user_ids = False
        self.assertFalse(self.release_channel.user_ids)
        self.picking.user_id = self.not_allowed_user
        self.assertEqual(self.picking.user_id, self.not_allowed_user)
