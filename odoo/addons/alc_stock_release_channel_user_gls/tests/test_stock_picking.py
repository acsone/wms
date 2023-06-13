# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_stock_release_channel_user.tests.common import (
    TestStockPickingCommon,
)
from odoo.addons.delivery_carrier_label_gls.tests.common import TestGLS


class TestStockPicking(TestStockPickingCommon, TestGLS):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        vals_gls_product = {"type": "service", "name": "Name ship GLS"}
        cls.gls_product = cls.env["product.product"].create(vals_gls_product)
        carrier_vals = cls._get_gls_carrier_vals()
        carrier_vals["product_id"] = cls.gls_product.id
        cls.gls_carrier = cls.env["delivery.carrier"].create(carrier_vals)
        cls.picking.write({"carrier_id": cls.gls_carrier.id})

    def test_00(self):
        """
        DATA:

            A release channel with 2 users
            A picking without user
        Test case:
            1. Assign a user part of the list of release channel users
            2. Assign on user not in the list of release channel users
        Expected result:
            1. user is assigned to the picking
            2. The user not part of the release channel is assigned as well because the
            picking is gls
        """
        self.picking.user_id = self.user_1
        self.assertEqual(self.picking.user_id, self.user_1)
        self.picking.user_id = self.not_allowed_user
