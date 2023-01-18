# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields

from .common import TestPricelistDiscountCommon

_logger = logging.getLogger(__name__)


class TestPricelistDiscount(TestPricelistDiscountCommon):
    def test_onchange_partner(self):
        partner = self.env["res.partner"].create(
            {"name": "Unittest other partner", "ref": "99584783994"}
        )
        sale = self.env["sale.order"].create({"partner_id": partner.id})

        self.assertFalse(sale.supplier_promotion_allowed)
        self.assertFalse(sale.discount_pricelist_ids)

        sale.partner_id = self.partner
        sale.onchange_partner_id_discount_pricelist()

        self.assertTrue(sale.supplier_promotion_allowed)
        self.assertEqual(self.discount_pricelist_id, sale.discount_pricelist_ids)

    def test_sale_discounts(self):
        # discounts are computed if not provided into the line info

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(10, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)

        self.assertEqual(90, self.sol_p1.price_subtotal)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)

        self.assertEqual(432, self.sale.amount_total)

    def test_sale_discounts_tax_excluded(self):
        self.tax.amount = 20

        for line in self.sale.order_line:

            line.onchange_product_id_reset_discount()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(10, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)

        self.assertEqual(90, self.sol_p1.price_subtotal)
        self.assertEqual(18, self.sol_p1.price_tax)
        self.assertAlmostEqual(108, self.sol_p1.price_total)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)
        self.assertEqual(68.4, self.sol_p2.price_tax)
        self.assertAlmostEqual(410.4, self.sol_p2.price_total)

        self.assertEqual(518.4, self.sale.amount_total)

    def test_sale_discounts_tax_included(self):
        self.tax.amount = 20
        self.tax.price_include = True

        for line in self.sale.order_line:

            line.onchange_product_id_reset_discount()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(10, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)

        self.assertEqual(75, self.sol_p1.price_subtotal)
        self.assertEqual(15, self.sol_p1.price_tax)
        self.assertAlmostEqual(90, self.sol_p1.price_total)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(285, self.sol_p2.price_subtotal)
        self.assertEqual(57, self.sol_p2.price_tax)
        self.assertAlmostEqual(342, self.sol_p2.price_total)

        self.assertEqual(432, self.sale.amount_total)

    def test_no_supplier_promotion(self):
        self.sale.supplier_promotion_allowed = False

        for line in self.sale.order_line:

            line.onchange_product_id_reset_discount()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(0, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)

        self.assertEqual(100, self.sol_p1.price_subtotal)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(0, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 190 * 2
        self.assertEqual(380, self.sol_p2.price_subtotal)

        self.assertEqual(480, self.sale.amount_total)

    def test_manually_change_unit_price(self):
        self.sol_p2.onchange_product_id_reset_discount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)

        # Change unit price
        self.sol_p2.price_unit = 150

        self.assertEqual(150, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(256.5, self.sol_p2.price_subtotal)

    def test_manually_change_discount(self):
        self.sol_p2.onchange_product_id_reset_discount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(10, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 171 * 2
        self.assertEqual(342, self.sol_p2.price_subtotal)

        # Change supplier promotion
        self.sol_p2.discount2 = 8.24
        self.sol_p2._compute_amount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(8.24, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 174.34 * 2
        self.assertEqual(348.68, self.sol_p2.price_subtotal)

        # Change alcyon discount
        self.sol_p2.discount3 = 3.83
        self.sol_p2._compute_amount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(8.24, self.sol_p2.discount2)
        self.assertEqual(3.83, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 174.34 * 2
        self.assertEqual(353, self.sol_p2.price_subtotal)

        # Change both
        self.sol_p2.discount2 = 20
        self.sol_p2.discount3 = 10
        self.sol_p2._compute_amount()

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(20, self.sol_p2.discount2)
        self.assertEqual(10, self.sol_p2.discount3)

        # There is 2 p2 in sale order so subtotal = 174.34 * 2
        self.assertEqual(288, self.sol_p2.price_subtotal)

        # Change quantity
        self.sol_p2.product_uom_qty = 1

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(20, self.sol_p2.discount2)
        self.assertEqual(10, self.sol_p2.discount3)

        self.assertEqual(144, self.sol_p2.price_subtotal)

        # Bug when only alcyon was filled
        # (And discount3 should not be recompute)
        self.sol_p2.price_unit = 0.46
        self.sol_p2.discount2 = 0
        self.sol_p2.discount3 = 5
        self.sol_p2._compute_amount()

        self.assertEqual(0.46, self.sol_p2.price_unit)
        self.assertEqual(0, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        self.assertEqual(0.44, self.sol_p2.price_subtotal)

    def test_create_invoice(self):
        self.tax.amount = 20

        for line in self.sale.order_line:

            line.onchange_product_id_reset_discount()

        self.sale.action_confirm()

        invoice = self.sale._create_invoices(final=True)
        self.assertEqual(1, len(invoice))
        self.assertEqual(518.4, self.sale.amount_total)
        self.assertEqual(86.4, self.sale.amount_tax)

        # Check invoice

        # Check lines
        line1 = invoice.invoice_line_ids.filtered(lambda l: l.product_id == self.p1)
        self.assertEqual(100, line1.price_unit)
        self.assertEqual(10, line1.discount2)
        self.assertEqual(0, line1.discount3)
        if line1.price_subtotal != 90:
            _logger.info("""=======Mythic bug is back this is a debug info=======""")
            _logger.info(
                """price_unit: %s
                price_subtotal:%s
                discount: %s
                discount2: %s,
                discount3: %s""",
                line1.price_unit,
                line1.price_subtotal,
                line1.discount,
                line1.discount2,
                line1.discount3,
            )
            _logger.info("""=======End of debug info=======""")
        self.assertEqual(90, line1.price_subtotal)

        line2 = invoice.invoice_line_ids.filtered(lambda l: l.product_id == self.p2)
        self.assertEqual(200, line2.price_unit)
        self.assertEqual(10, line2.discount2)
        self.assertEqual(5, line2.discount3)
        self.assertEqual(342, line2.price_subtotal)

        # Check totals
        self.assertEqual(518.4, invoice.amount_total)
        self.assertEqual(86.4, invoice.amount_tax)

    def test_coverage(self):
        """Test special cases for coverage."""

        # Supplier promotion 100%
        self.supplierinfo1.discount_sale = 100
        self.supplierinfo2.discount_sale = 100
        self.tax.amount = 20

        for line in self.sale.order_line:

            line.onchange_product_id_reset_discount()

        self.assertEqual(100, self.sol_p1.price_unit)
        self.assertEqual(100, self.sol_p1.discount2)
        self.assertEqual(0, self.sol_p1.discount3)

        self.assertEqual(0, self.sol_p1.price_subtotal)
        self.assertEqual(0, self.sol_p1.price_tax)
        self.assertAlmostEqual(0, self.sol_p1.price_total)

        self.assertEqual(200, self.sol_p2.price_unit)
        self.assertEqual(100, self.sol_p2.discount2)
        self.assertEqual(5, self.sol_p2.discount3)

        self.assertEqual(0, self.sol_p2.price_subtotal)
        self.assertEqual(0, self.sol_p2.price_tax)
        self.assertAlmostEqual(0, self.sol_p2.price_total)

        self.assertEqual(0, self.sale.amount_total)

    def test_commercial_fields(self):
        sub_partner = self.env["res.partner"].create(
            {
                "parent_id": self.partner.id,
                "ref": "234788894934",
                "name": "Unittest sub partner",
                "supplier_promotion_sale_allowed": True,
            }
        )

        self.sale.write(
            {
                "supplier_promotion_allowed": False,
                "discount_pricelist_ids": [(5, 0, 0)],
                "partner_id": sub_partner.id,
            }
        )

        self.sale.onchange_partner_id_discount_pricelist()
        self.assertTrue(self.sale.supplier_promotion_allowed)
        self.assertEqual(self.discount_pricelist_id, self.sale.discount_pricelist_ids)

    def test_select_seller(self):
        """Test the method _select_seller.

        and _select_seller.

        Default price: 100€
        Promo 1 (2018-01-01 -> 2018-03-31)
            Min sale: 0 - min purchase: 0
                * - 10% on sale
                * - 15% on purchase
            Min sale: 0 - min purchase: 100
                * - 10% on sale
                * - 20% on purchase

        Promo 2 (2018-04-01 -> 2018-06-30)
            Min sale: 0 - min purchase: 0
                * - 11% on sale
                * - 13% on purchase
            Min sale: 25 - min purchase: 0
                * - 11.5% on sale
                * - 13% on purchase
            Min sale: 50 - min purchase: 0
                * - 14% on sale
                * - 13% on purchase
        Promo 3 (2018-08-01 -> 2018-12-31)
            Min sale: 0 - min purchase: 0
                * - 8% on sale
                * - 10% on purchase
        """

        sinfo_model = self.env["product.supplierinfo"]
        sinfo_model.search(
            [("product_tmpl_id", "=", self.p1.product_tmpl_id.id)]
        ).unlink()

        # Create the default price
        default_promo = sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.p1.product_tmpl_id.id,
                "price": 100,
                "sequence": 1000,
            }
        )

        # Promo 1 (2018-01-01 -> 2018-03-31)
        promo_1 = sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.p1.product_tmpl_id.id,
                "date_start": fields.Date.from_string("2018-01-01"),
                "date_end": fields.Date.from_string("2018-03-31"),
                "discount_sale": 10,
                "discount_purchase": 15,
                "price": 100,
            }
        )
        # Promo 1 (2018-01-01 -> 2018-03-31) with min_qty == 100
        promo_1_min_100 = sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.p1.product_tmpl_id.id,
                "date_start": fields.Date.from_string("2018-01-01"),
                "date_end": fields.Date.from_string("2018-03-31"),
                "min_qty": 100,
                "discount_sale": 10,
                "discount_purchase": 20,
                "price": 100,
            }
        )

        # Promo 2 (2018-04-01 -> 2018-06-30)
        promo_2 = sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.p1.product_tmpl_id.id,
                "date_start": fields.Date.from_string("2018-04-01"),
                "date_end": fields.Date.from_string("2018-06-30"),
                "discount_sale": 11,
                "discount_purchase": 13,
                "price": 100,
            }
        )

        # Promo 2 (2018-04-01 -> 2018-06-30) with min_qty_sale == 25
        promo_2_min_sale_25 = sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.p1.product_tmpl_id.id,
                "date_start": fields.Date.from_string("2018-04-01"),
                "date_end": fields.Date.from_string("2018-06-30"),
                "min_qty_sale": 25,
                "discount_sale": 11.5,
                "discount_purchase": 13,
                "price": 100,
            }
        )

        # Promo 2 (2018-04-01 -> 2018-06-30) with min_qty_sale == 50
        promo_2_min_sale_50 = sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.p1.product_tmpl_id.id,
                "date_start": fields.Date.from_string("2018-04-01"),
                "date_end": fields.Date.from_string("2018-06-30"),
                "min_qty_sale": 50,
                "discount_sale": 14,
                "discount_purchase": 13,
                "price": 100,
            }
        )

        # Promo 3 (2018-08-01 -> 2018-12-31)
        promo_3 = sinfo_model.create(
            {
                "partner_id": self.supplier.id,
                "product_tmpl_id": self.p1.product_tmpl_id.id,
                "date_start": fields.Date.from_string("2018-08-01"),
                "date_end": fields.Date.from_string("2018-12-31"),
                "discount_sale": 8,
                "discount_purchase": 10,
                "price": 100,
            }
        )

        # Test default promo
        promo = self.p1._select_seller(
            partner_id=self.supplier,
            quantity=20,
            date=fields.Date.to_date("2019-01-01"),
        )
        self.assertEqual(promo, default_promo)

        # Test promo 1
        promo = self.p1._select_seller(
            partner_id=self.supplier,
            quantity=20,
            date=fields.Date.to_date("2018-01-01"),
        )
        self.assertEqual(promo, promo_1)

        # Test promo 2
        promo = self.p1._select_seller(
            partner_id=self.supplier,
            quantity=20,
            date=fields.Date.to_date("2018-05-01"),
        )
        self.assertEqual(promo, promo_2)

        # Test promo 3
        promo = self.p1._select_seller(
            partner_id=self.supplier,
            quantity=20,
            date=fields.Date.to_date("2018-12-31"),
        )
        self.assertEqual(promo, promo_3)

        # Test promo 1 with min (purchase) 100
        promo = self.p1._select_seller(
            partner_id=self.supplier,
            quantity=100,
            date=fields.Date.to_date("2018-01-01"),
        )
        self.assertEqual(promo, promo_1_min_100)

        # Test promo 2 with min (sale) 40
        promo = self.p1._select_seller(
            partner_id=self.supplier,
            quantity=40,
            date=fields.Date.to_date("2018-05-01"),
        )
        self.assertEqual(promo, promo_2_min_sale_25)

        # Test promo 2 with min (sale) 120
        promo = self.p1._select_seller(
            partner_id=self.supplier,
            quantity=120,
            date=fields.Date.to_date("2018-05-01"),
        )
        self.assertEqual(promo, promo_2_min_sale_50)

        # Test promo 2 with min (purchase) 40 (method _select_seller)
        promo = self.p1._select_seller(
            partner_id=self.supplier,
            quantity=40,
            date=fields.Date.to_date("2018-05-01"),
        )
        self.assertEqual(promo, promo_2_min_sale_25)

    def test_multiple_min_qty(self):
        vals_item_10 = {
            "pricelist_id": self.discount_pricelist_id.id,
            "applied_on": "2_product_category",
            "categ_id": self.category.parent_id.id,
            "compute_price": "percentage",
            "min_quantity": 10,
            "percent_price": 10,
        }
        vals_item_20 = dict(vals_item_10, min_quantity=20, percent_price=20)

        self.env["product.pricelist.item"].create(vals_item_10)
        self.env["product.pricelist.item"].create(vals_item_20)

        line = self.sol_p2
        line._compute_discount_item_id()
        line.onchange_product_id_reset_discount()
        self.assertEqual(5, line.discount3)

        line.product_uom_qty = 10
        line._compute_discount_item_id()
        line.onchange_product_id_reset_discount()
        self.assertEqual(10, line.discount3)

        line.product_uom_qty = 20
        line._compute_discount_item_id()
        line.onchange_product_id_reset_discount()
        self.assertEqual(20, line.discount3)
