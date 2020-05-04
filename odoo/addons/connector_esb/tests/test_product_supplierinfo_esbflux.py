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

    def test_create_promotion_buyx_gety(self):
        """Check values on created record."""
        r = self.supinfo.create(
            {
                "name": self.partner.id,
                "product_tmpl_id": self.prod_2.id,
                "ratio_main_product": 5,
                "ratio_promotional_product": 1,
                "date_start": self.date_start,
                "date_end": self.date_end,
            }
        )
        r_flux = self.esbflux.search(
            [("real_id", "=", r.id), ("flux", "=", "buyxgety")]
        )
        self.assertEqual(r.ratio_main_product, r_flux.ratio_main_product)
        self.assertEqual(r.ratio_promotional_product, r_flux.ratio_promotional_product)
        self.assertEqual(r.product_tmpl_id.id, r_flux.product_tmpl_id.id)
        self.assertEqual(r.date_start, r_flux.date_start)
        self.assertEqual(r.date_end, r_flux.date_end)
        self.assertEqual(r_flux.flux, "buyxgety")
        self.assertEqual(r_flux.action, "create")

    def test_update_promotion_buyx_gety(self):
        """Check the delete/create action on update of record"""
        self.esbflux.search([]).unlink()
        previous_ratio = self.supinfo_1.ratio_main_product
        new_ratio = 9
        self.supinfo_1.ratio_main_product = new_ratio
        r = self.esbflux.search(
            [
                ("real_id", "=", self.supinfo_1.id),
                ("flux", "=", "buyxgety"),
                ("action", "=", "delete"),
            ]
        )
        # Check that the delete action entry is correct
        # It should contain the previous values
        self.assertEqual(r.ratio_main_product, previous_ratio)
        self.assertEqual(
            r.ratio_promotional_product, self.supinfo_1.ratio_promotional_product
        )
        self.assertEqual(r.product_tmpl_id.id, self.supinfo_1.product_tmpl_id.id)
        self.assertEqual(r.date_start, self.supinfo_1.date_start)
        self.assertEqual(r.date_end, self.supinfo_1.date_end)
        # Check that the new create action entry is correct
        # It should contain the new values
        r = self.esbflux.search(
            [("real_id", "=", self.supinfo_1.id), ("action", "=", "create")]
        )
        self.assertEqual(r.ratio_main_product, new_ratio)
        self.assertEqual(
            r.ratio_promotional_product, self.supinfo_1.ratio_promotional_product
        )
        self.assertEqual(r.product_tmpl_id.id, self.supinfo_1.product_tmpl_id.id)
        self.assertEqual(r.date_start, self.supinfo_1.date_start)
        self.assertEqual(r.date_end, self.supinfo_1.date_end)
        self.assertEqual(r.flux, "buyxgety")
        self.assertEqual(r.action, "create")

    def test_create_update_delete_promotion_buyx_gety(self):
        r = self.supinfo.create(
            {
                "name": self.partner.id,
                "product_tmpl_id": self.prod_2.id,
                "ratio_main_product": 5,
                "ratio_promotional_product": 1,
                "date_start": self.date_start,
                "date_end": self.date_end,
            }
        )
        qty = self.esbflux.search_count(
            [("real_id", "=", r.id), ("flux", "=", "buyxgety")]
        )
        # A create record is add in the table
        self.assertEqual(qty, 1)
        # Modifying the promotion...
        r.ratio_main_product = 12
        qty = self.esbflux.search_count(
            [("real_id", "=", r.id), ("flux", "=", "buyxgety")]
        )
        # It creates a delete and a create record
        self.assertEqual(qty, 3)
        # Changing an unrelated value...
        r.price = 12
        qty = self.esbflux.search_count(
            [("real_id", "=", r.id), ("flux", "=", "buyxgety")]
        )
        # Should not add rows
        self.assertEqual(qty, 3)
        # Changing an unrelated value...
        r.price = 12
        qty = self.esbflux.search_count(
            [("real_id", "=", r.id), ("flux", "=", "buyxgety")]
        )
        # Should not add rows
        self.assertEqual(qty, 3)

    def test_create_update_delete_special_promotion(self):
        r = self.supinfo.create(
            {
                "name": self.partner.id,
                "product_tmpl_id": self.prod_2.id,
                "discount_sale": 10,
                "date_start": self.date_start,
                "date_end": self.date_end,
            }
        )
        qty = self.esbflux.search_count(
            [("real_id", "=", r.id), ("flux", "=", "specialpromotion")]
        )
        # A create record is added in the table
        self.assertEqual(qty, 1)
        # Modifying the promotion...
        r.discount_sale = 12
        qty = self.esbflux.search_count(
            [("real_id", "=", r.id), ("flux", "=", "specialpromotion")]
        )
        # It creates a delete and a create record
        self.assertEqual(qty, 3)
        # Modifying the end date
        r.date_end = fields.Datetime.to_string(datetime.now() + relativedelta(month=4))
        qty = self.esbflux.search_count(
            [("real_id", "=", r.id), ("flux", "=", "specialpromotion")]
        )
        # It adds a delete and a create record
        self.assertEqual(qty, 5)
        # Changing an unrelated value...
        r.price = 12
        qty = self.esbflux.search_count(
            [("real_id", "=", r.id), ("flux", "=", "specialpromotion")]
        )
        # Should not add rows
        self.assertEqual(qty, 5)

    def test_both_promotion_updated_same_time(self):
        """Create and update both promotion at the same time"""
        r = self.supinfo.create(
            {
                "name": self.partner.id,
                "product_tmpl_id": self.prod_2.id,
                "ratio_main_product": 5,
                "ratio_promotional_product": 1,
                "discount_sale": 4,
                "date_start": self.date_start,
                "date_end": self.date_end,
            }
        )
        qty = self.esbflux.search_count([("real_id", "=", r.id)])
        self.assertEqual(qty, 2)
        # Lets be generous and give more free products and better discount
        # Changing both promotion at the same time
        r.write({"ratio_promotional_product": 2, "discount_sale": 6})
        qty = self.esbflux.search_count([("real_id", "=", r.id)])
        self.assertEqual(qty, 6)
