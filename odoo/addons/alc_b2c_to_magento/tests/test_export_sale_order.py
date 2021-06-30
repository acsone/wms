# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock

from .common import ExportB2cCommon, post_ret_status


class TestExportSaleOrder(ExportB2cCommon):
    def test_map_data(self):
        """
        Data:
            A sale order with sale_channel set to chronovet
        Test case:
            Map SO info to ESB
        Expected result;
            The customer id into the exported data is the generic b2c partner
            The sale_channel is 01 (phone)
        """
        expected_partner = self.env.ref("alc_b2c_partner.b2c_customer")
        with self.backend.work_on("sale.order") as work:
            mapper = work.component(usage="export.mapper")
            values = mapper.map_record(self.order).values()
        self.assertEqual(values["customer_id"], expected_partner.ref)
        self.assertEqual(values["channel"], "01")

    @mock.patch("requests.post", side_effect=post_ret_status)
    def test_export(self, post):
        """
        Data:
            A B2C sale order
        Test case:
            Export the SO to magento
        Expected result;
            The SO is exported
        """
        # Test export of a sale order catching the put request.
        self.order.action_confirm()
        with self.backend.work_on("sale.order") as work:
            exporter = work.component(usage="record.exporter")
            exporter.run(self.order)
        post.assert_called_once()
        self.assertEqual(self.order.esb_ref, "1000000348")
