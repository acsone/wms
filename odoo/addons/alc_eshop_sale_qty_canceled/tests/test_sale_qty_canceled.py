# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSaleQtyCanceled(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleQtyCanceled, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
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
        cls.so = cls.env["sale.order"].create(so_vals)
        cls.so.action_confirm()
        # "internal" picking type is required by the cancel wizard since
        # it's designed to work in a 2 steps picking
        cls.so.picking_ids.picking_type_id.code = "internal"
        cls.cancel_wiz = cls.env["sale.order.line.cancel"].create({})

    def setUp(self):
        super(TestSaleQtyCanceled, self).setUp()
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="sales")

    def test_info(self):
        info = self.service.search()
        self.assertEqual(1, info["size"])
        order_info = info["data"][0]
        line_info = order_info["lines"]["items"][0]
        self.assertEqual(0, line_info["qty_canceled"])
        self.cancel_wiz.with_context(
            active_id=self.so.order_line.id
        ).cancel_remaining_qty()
        info = self.service.search()
        order_info = info["data"][0]
        line_info = order_info["lines"]["items"][0]
        self.assertEqual(100, line_info["qty_canceled"])
