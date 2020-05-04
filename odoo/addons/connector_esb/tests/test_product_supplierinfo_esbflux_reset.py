# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class ProductSupplierInfoEsbFluxTestCase(TransactionCase):
    def setUp(self):
        super(ProductSupplierInfoEsbFluxTestCase, self).setUp()
        self.supinfo = self.env["product.supplierinfo"]
        self.esbflux = self.env["product.supplierinfo.esbflux"]
        self.partner = self.env.ref("base.res_partner_1")
        self.prod_1 = self.env.ref("product.product_product_1_product_template")
        self.prod_2 = self.env.ref("product.product_product_2_product_template")
        self.date_start = fields.Datetime.to_string(
            datetime.now() - relativedelta(years=1)
        )
        self.date_end = fields.Datetime.to_string(
            datetime.now() + relativedelta(years=1)
        )
        self.old_date_start = fields.Datetime.to_string(
            datetime.now() - relativedelta(years=1, days=1)
        )
        # Valid promotion
        self.supinfo_1 = self.supinfo.create(
            {
                "name": self.partner.id,
                "product_tmpl_id": self.prod_1.id,
                "ratio_main_product": 5,
                "ratio_promotional_product": 1,
                "date_start": self.date_start,
                "date_end": self.date_end,
            }
        )
        # Old promotion not more valid
        self.supinfo_2 = self.supinfo.create(
            {
                "name": self.partner.id,
                "product_tmpl_id": self.prod_1.id,
                "ratio_main_product": 5,
                "ratio_promotional_product": 1,
                "date_start": self.old_date_start,
                "date_end": self.old_date_start,
            }
        )
        self.supinfo_3 = self.supinfo.create(
            {
                "name": self.partner.id,
                "product_tmpl_id": self.prod_2.id,
                "discount_sale": 4,
                "date_start": self.date_start,
                "date_end": self.date_end,
            }
        )
        # Set some last export date to check that they will be reset
        self.flux_ids = [
            "connector_esb.esb_timestamp_special_promotion",
            "connector_esb.esb_timestamp_buyx_gety",
        ]

        now_time = fields.Datetime.to_string(datetime.now())
        for flux in self.flux_ids:
            self.env.ref(flux).last_export = now_time

    def test_reset_esbflux_table(self):
        records = self.esbflux.search([(1, "=", 1)])
        assert len(records) > 0
        self.esbflux.reset_flux()
        records = self.esbflux.search([(1, "=", 1)])
        assert len(records) == 2
        # Check the buyxgety promo is correct
        r_flux = self.esbflux.search(
            [("ratio_main_product", "=", 5), ("flux", "=", "buyxgety")]
        )
        self.assertEqual(self.supinfo_1.ratio_main_product, r_flux.ratio_main_product)
        self.assertEqual(
            self.supinfo_1.ratio_promotional_product, r_flux.ratio_promotional_product
        )
        self.assertEqual(self.supinfo_1.product_tmpl_id.id, r_flux.product_tmpl_id.id)
        self.assertEqual(self.supinfo_1.date_start, r_flux.date_start)
        self.assertEqual(self.supinfo_1.date_end, r_flux.date_end)
        self.assertEqual(r_flux.flux, "buyxgety")
        self.assertEqual(r_flux.action, "create")
        # Check the buyxgety promo is correct
        r_flux = self.esbflux.search(
            [("discount_sale", "=", 4), ("flux", "=", "specialpromotion")]
        )
        self.assertEqual(self.supinfo_3.ratio_main_product, 0)
        self.assertEqual(self.supinfo_3.ratio_promotional_product, 0)
        self.assertEqual(self.supinfo_3.product_tmpl_id.id, r_flux.product_tmpl_id.id)
        self.assertEqual(self.supinfo_3.discount_sale, r_flux.discount_sale)
        self.assertEqual(self.supinfo_3.date_start, r_flux.date_start)
        self.assertEqual(self.supinfo_3.date_end, r_flux.date_end)
        self.assertEqual(r_flux.flux, "specialpromotion")
        self.assertEqual(r_flux.action, "create")
        for flux in self.flux_ids:
            assert self.env.ref(flux).last_export is False
