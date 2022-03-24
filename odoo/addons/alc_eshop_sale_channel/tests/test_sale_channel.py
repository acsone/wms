# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSaleChannel(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleChannel, cls).setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        so_vals = {
            "partner_id": cls.partner.id,
        }
        if "shopinvader.backend" in cls.env:
            so_vals["shopinvader_backend_id"] = cls.env.ref("shopinvader.backend_1").id
        cls.so_no_channel = cls.env["sale.order"].create(so_vals)

    def setUp(self):
        super(TestSaleChannel, self).setUp()
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="sales")

    def test_search(self):
        info = self.service.search()
        self.assertEqual(0, info["size"])
        for channel in self.env["sale.order"]._get_sale_channels():
            self.so_no_channel.write({"sale_channel": channel})
            size = (
                1
                if channel in self.env["sale.order"]._get_sale_channels_internal()
                else 0
            )
            info = self.service.search()
            self.assertEqual(
                size, info["size"], "Bad result for channel '%s'" % channel
            )
            if size:
                json = info["data"][0]
                self.assertEqual(channel, json["sale_channel"])
