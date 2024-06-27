# Copyright 2022 ACSONE SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo.addons.stock_release_channel.tests.common import ReleaseChannelCase


class TestReleaseChannelPropagation(ReleaseChannelCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._update_qty_in_location(cls.wh.lot_stock_id, cls.product1, 20.0)
        cls._update_qty_in_location(cls.wh.lot_stock_id, cls.product2, 20.0)
        cls.wh.out_type_id.propagate_to_pickings_chain = True

    def test_channel_internal_propagation(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "stock_release_channel_process_end_time.stock_release_use_channel_end_date",
            True,
        )
        self.default_channel.process_end_time = 10.0
        self.product = self.product1
        pickings_before = self.env["stock.picking"].search(
            [("product_id", "=", self.product.id)]
        )
        self._run_customer_procurement()
        pickings_after = (
            self.env["stock.picking"].search([("product_id", "=", self.product.id)])
            - pickings_before
        )
        pickings_after.assign_release_channel()
        pickings_after.release_available_to_promise()

        pickings_internal = (
            self.env["stock.picking"].search([("product_id", "=", self.product.id)])
            - pickings_after
            - pickings_before
        )
        self.assertEqual(
            pickings_internal.scheduled_date,
            pickings_internal.release_channel_id.process_end_date,
        )
        return pickings_internal
