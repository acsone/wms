# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSalePaymentInfo(CommonCase):
    @classmethod
    def setUpClass(cls):
        super(TestSalePaymentInfo, cls).setUpClass()
        cls.partner = cls.env.ref("shopinvader.partner_1")
        cls.payment_mode = cls.env.ref("account_payment_mode.payment_mode_inbound_dd1")
        so_vals = {
            "partner_id": cls.partner.id,
            "payment_mode_id": cls.payment_mode.id,
        }
        if "shopinvader.backend" in cls.env:
            so_vals["shopinvader_backend_id"] = cls.env.ref("shopinvader.backend_1").id
        if "sale_channel" in cls.env["sale.order"]._fields:
            so_vals["sale_channel"] = cls.env[
                "sale.order"
            ]._get_sale_channels_internal()[0]
        cls.so = cls.env["sale.order"].create(so_vals)

    def setUp(self):
        super(TestSalePaymentInfo, self).setUp()
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="sales")

    def test_search_info(self):
        info = self.service._convert_one_sale(self.so)
        self.assertIn("payment", info)
        self.assertDictEqual(
            {"mode": {"id": self.payment_mode.id, "name": self.payment_mode.name}},
            info["payment"],
        )
