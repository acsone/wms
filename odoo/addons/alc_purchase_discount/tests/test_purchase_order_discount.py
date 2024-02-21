# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import Command, fields
from odoo.tests.common import Form, TransactionCase


class TestPurchaseOrderDiscount(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.product = cls.env["product.product"].create({"name": "Product 1"})
        cls.product2 = cls.env["product.product"].create({"name": "Product 2"})
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
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        buy_route = cls.warehouse.buy_pull_id.route_id
        cls.product2.route_ids = buy_route

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

    @freeze_time("2023-04-03")
    def test_po_create_from_procurement(self):
        self.env["stock.warehouse.orderpoint"].create(
            {
                "warehouse_id": self.warehouse.id,
                "product_id": self.product2.id,
                "company_id": self.warehouse.company_id.id,
                "product_min_qty": 0,
                "product_max_qty": 0,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_uom": self.product2.uom_id.id,
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.supplier.id,
                "discount": 10,
                "product_tmpl_id": self.product2.product_tmpl_id.id,
                "price": 10,
            }
        )
        self.supplier.supplier_discount = 15
        ship = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.ref("stock.picking_type_out"),
                "move_ids": [
                    Command.create(
                        {
                            "name": "Delivery move",
                            "product_id": self.product2.id,
                            "product_uom_qty": 100,
                            "product_uom": self.product2.uom_id.id,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "location_dest_id": self.customer_location.id,
                            "picking_type_id": self.warehouse.in_type_id.id,
                        }
                    )
                ],
            }
        )
        ship.action_confirm()
        self.env["procurement.group"].run_scheduler()
        po_line = self.product2.purchase_order_line_ids
        self.assertEqual(po_line.product_qty, 100)
        self.assertEqual(po_line.partner_id, self.supplier)
        self.assertEqual(po_line.discount_global, 15)
        self.assertEqual(po_line.promotion_supplier, 10)
        self.assertEqual(po_line.discount, 23.5)
        self.assertEqual(po_line.price_subtotal, 765)
        self.assertEqual(
            po_line.order_id.date_order,
            fields.Datetime.to_datetime("2023-04-03 12:00:00"),
        )

    def test_price_recompute_at_date_order_change(self):
        self.env["product.supplierinfo"].create(
            [
                {
                    "partner_id": self.supplier.id,
                    "price": 101,
                    "discount": 5,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "date_start": "2023-01-01",
                    "date_end": "2023-12-31",
                    "min_qty": 20,
                },
                {
                    "partner_id": self.supplier.id,
                    "price": 151,
                    "discount": 10,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "date_start": "2023-01-01",
                    "date_end": "2023-12-31",
                },
                {
                    "partner_id": self.supplier.id,
                    "price": 201,
                    "discount": 15,
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "date_start": "2024-01-01",
                    "date_end": "2024-12-31",
                },
            ]
        )
        self.assertEqual(self.po_line.price_unit, 15)
        self.assertEqual(self.po_line.discount, 0)
        self.po.date_order = "2023-06-01"
        self.assertEqual(self.po_line.price_unit, 151)
        self.assertEqual(self.po_line.discount, 10)
        self.po_line.product_qty = 21
        self.assertEqual(self.po_line.price_unit, 101)
        self.assertEqual(self.po_line.discount, 5)
        self.po.date_order = "2024-06-01"
        self.assertEqual(self.po_line.price_unit, 201)
        self.assertEqual(self.po_line.discount, 15)
