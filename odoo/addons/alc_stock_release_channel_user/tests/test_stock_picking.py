# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import TestStockPickingCommon


class TestStockPicking(TestStockPickingCommon):
    def test_00(self):
        """
        DATA:

            A release channel with 2 users
            A picking without user
        Test case:
            1. Assign an user part of the list of release channel users
            2. Assign on user not in the list of release channel users
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

            A release channel with 2 users
            A picking with 1 allowed user
        Test case:
            Remove the user linked to the picking from the list of
            users on the release channel
        Expected result:
            No error is raised ans the user is still assigned to the
            picking
        """
        self.picking.user_id = self.user_1
        self.release_channel.user_ids = False
        self.assertFalse(self.release_channel.user_ids)
        self.picking.user_id = self.not_allowed_user
        self.assertEqual(self.picking.user_id, self.not_allowed_user)
