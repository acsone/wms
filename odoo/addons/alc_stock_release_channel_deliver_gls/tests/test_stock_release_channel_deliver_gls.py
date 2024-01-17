# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.alc_stock_release_channel_deliver.tests.common import (
    TestStockReleaseChannelDeliverCommon,
)
from odoo.addons.delivery_carrier_label_gls.tests.common import TestGLS


class TestStockReleaseChannelDeliverGls(TestStockReleaseChannelDeliverCommon, TestGLS):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.company_id.shipment_advice_run_in_queue_job = True
        vals_gls_product = {"type": "service", "name": "Name ship GLS"}
        cls.gls_product = cls.env["product.product"].create(vals_gls_product)
        carrier_vals = cls._get_gls_carrier_vals()
        carrier_vals["product_id"] = cls.gls_product.id
        cls.gls_carrier = cls.env["delivery.carrier"].create(carrier_vals)
        cls.pickings.write({"carrier_id": cls.gls_carrier.id})

    def test_00(self):
        """The delivery of gls picking should be manual, the delivery action returns.

        the picking list
        """
        self._do_internal_pickings()
        action = self.channel.action_delivering()
        self.assertEqual(action.get("xml_id"), "stock.action_picking_tree_all")
        self.assertEqual(set(action.get("domain")[0][2]), set(self.pickings.ids))
        self.assertEqual(action.get("res_model"), "stock.picking")
