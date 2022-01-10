# -*- coding: utf-8 -*-
# Copyright 2021 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import SavepointCase


class TestMrpRepair(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMrpRepair, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777878"}
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.location_sav = cls.env.ref("alc_mrp_repair.sav_stock_location")

        cls.p1 = cls.env["product.product"].create(
            {
                "name": "test product",
                "sale_ok": True,
                "type": "product",
                "barcode": "XXX0001",
                "default_code": "12345",
            }
        )

    def test_00_create_repair_check_default_location(self):
        repair = self.env["mrp.repair"].create(
            {
                "name": "repair 01",
                "product_id": self.p1.id,
                "product_uom": self.p1.uom_id.id,
                "partner_id": self.partner1.id,
            }
        )
        self.assertEqual(repair.location_id.id, self.location_sav.id)

    def test_01_repair_set_back_to_draft(self):
        repair = self.env["mrp.repair"].create(
            {
                "name": "repair 01",
                "product_id": self.p1.id,
                "product_uom": self.p1.uom_id.id,
                "partner_id": self.partner1.id,
            }
        )
        self.assertEqual(repair.state, "draft")

        repair.action_repair_confirm()
        self.assertEqual(repair.state, "confirmed")

        repair.action_repair_cancel_draft()
        self.assertEqual(repair.state, "draft")

    def test_02_repair_started_set_back_to_draft(self):
        repair = self.env["mrp.repair"].create(
            {
                "name": "repair 01",
                "product_id": self.p1.id,
                "product_uom": self.p1.uom_id.id,
                "partner_id": self.partner1.id,
            }
        )
        self.assertEqual(repair.state, "draft")

        repair.action_repair_confirm()
        self.assertEqual(repair.state, "confirmed")

        repair.action_repair_start()
        self.assertEqual(repair.state, "under_repair")

        with self.assertRaises(UserError):
            repair.action_repair_cancel_draft()
