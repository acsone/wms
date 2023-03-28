# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestStockPickingName(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.default_channel = cls.env.ref(
            "stock_release_channel.stock_release_channel_default"
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Partner Picking Test",
            }
        )

    def test_stock_picking_name(self):
        # Create a picking with a partner and a release channel
        self.picking = self.env["stock.picking"].create(
            {
                "name": "Picking 1",
                "release_channel_id": self.default_channel.id,
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )

        self.assertEqual(
            "Picking 1 - Partner Picking Test - Default", self.picking.display_name
        )
        # Create a picking with a partner
        self.picking = self.env["stock.picking"].create(
            {
                "name": "Picking 1",
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )

        self.assertEqual("Picking 1 - Partner Picking Test", self.picking.display_name)
        # Create a picking without partner and release channel
        self.picking = self.env["stock.picking"].create(
            {
                "name": "Picking 1",
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )

        self.assertEqual("Picking 1", self.picking.display_name)
        # Create a picking with a release channel
        self.picking = self.env["stock.picking"].create(
            {
                "name": "Picking 1",
                "release_channel_id": self.default_channel.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )

        self.assertEqual("Picking 1 - Default", self.picking.display_name)
