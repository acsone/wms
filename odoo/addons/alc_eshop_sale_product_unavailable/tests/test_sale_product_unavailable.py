# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSaleProductUnavailable(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleProductUnavailable, cls).setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        so_vals = {
            "partner_id": cls.partner.id,
            "order_line": [
                (0, 0, {"product_id": cls.product_1.id, "product_uom_qty": 100})
            ],
        }
        if "shopinvader.backend" in cls.env:
            so_vals["shopinvader_backend_id"] = cls.env.ref("shopinvader.backend_1").id
        if "sale_channel" in cls.env["sale.order"]._fields:
            so_vals["sale_channel"] = "web"
        cls.so_no_channel = cls.env["sale.order"].create(so_vals)

    def setUp(self):
        super(TestSaleProductUnavailable, self).setUp()
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="sales")

    def test_info(self):
        info = self.service.search()
        self.assertEqual(1, info["size"])
        order_info = info["data"][0]
        line_info = order_info["lines"]["items"][0]
        self.assertEqual(100.0, line_info["qty_unavailable"])
