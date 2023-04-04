# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import Form, TransactionCase


class TestPurchaseOrderDiscount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.product = cls.env["product.product"].create({"name": "Product 1"})
        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.supplier.id,
                "date_order": fields.Datetime.now(),
                "date_planned": fields.Datetime.now(),
            }
        )
        cls.po_line = cls.po.order_line.create(
            {
                "order_id": cls.po.id,
                "product_id": cls.product.id,
                "name": cls.product.name,
                "product_qty": 10,
                "product_uom": cls.env.ref("uom.product_uom_unit").id,
                "price_unit": 15,
            }
        )
        cls.po_line2 = cls.po_line.copy()
        cls.po.order_line.write({"taxes_id": False})

    def setUp(self):
        super().setUp()
        self.po_form = Form(self.po)

    def test_unit_price(self):
        self.assertEqual(self.po.amount_total, 300)
        with self.po_form.order_line.edit(0) as po_line_form:
            # Change the price_unit of my line
            po_line_form.price_unit = 10
            self.assertEqual(po_line_form.price_unit, 10)
            self.assertEqual(po_line_form.price_subtotal, 100)
            # Add a discount of 50% on the last line
            po_line_form.discount_global = 50
            self.assertEqual(po_line_form.price_subtotal, 50)
            # Add a pricelist discount of 10%
            # (this discount will be add to the discount of 50%)
            po_line_form.promotion_supplier = 10
            self.assertEqual(po_line_form.price_subtotal, 45)

    def test_promotion_supplier(self):
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "discount": 10,
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )
        with self.po_form.order_line.edit(0) as po_line_form:
            po_line_form.product_qty = 15
            self.assertEqual(po_line_form.promotion_supplier, 10)

    def test_supplier_discount(self):
        self.supplier.supplier_discount = 10
        with self.po_form.order_line.edit(0) as po_line_form:
            po_line_form.product_qty = 15
            self.assertEqual(po_line_form.discount_global, 10)
