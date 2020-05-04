# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .common import ESBXMLTestCase


class WSProductStockSKUTestCase(ESBXMLTestCase):
    def setUp(self):
        super(WSProductStockSKUTestCase, self).setUp()
        self.setup_records()

    @property
    def model(self):
        return self.env["product.product"]

    def change_product_qty(self, product, qty):
        self.env["stock.change.product.qty"].create(
            {"product_id": product.id, "new_quantity": qty}
        ).change_product_qty()

    def setup_records(self):
        self.product1 = self.model.create(
            {"name": "Product1", "default_code": "Product1"}
        )
        self.product2 = self.model.create(
            {"name": "Product2", "default_code": "Product2"}
        )
        self.product3 = self.model.create(
            {"name": "Product3", "default_code": "Product3"}
        )
        self.all_records = self.product1 + self.product2 + self.product3

        self.change_product_qty(self.product1, 20)
        self.change_product_qty(self.product2, 0)
        self.change_product_qty(self.product3, 15)

    def test_message(self):
        backend = self.env["esb.backend"].get_singleton()
        skus = self.all_records.mapped("default_code")
        with backend.work_on("product.product") as work:
            component = work.component("ws.message.product.stock.sku")
            result = component.get_message(skus)

        product_mapper = {
            "Product1": self.product1,
            "Product2": self.product2,
            "Product3": self.product3,
        }

        self.assertEqual(len(result), 3)
        for product_values in result:
            product = product_mapper[product_values["sku"]]
            qty = product_values["quantity"]
            self.assertEqual(product.immediately_usable_qty, qty)

        # Disable the product 1
        self.product1.sale_ok = False
        backend = self.env["esb.backend"].get_singleton()
        skus = self.all_records.mapped("default_code")
        with backend.work_on("product.product") as work:
            component = work.component("ws.message.product.stock.sku")
            result = component.get_message(skus)
        self.assertEqual(len(result), 2)

    def test_message_olalux(self):

        # Create the user Test Olalux
        olalux_user = self.env["res.users"].create(
            {"login": "test_olalux", "name": "Test Olalux", "is_for_olalux": True}
        )

        # Create the supplier Royal Canin if doesn't yet existing
        royal_canin_supplier = self.env["res.partner"].search(
            [("supplier", "=", True), ("ref", "=", "78650")]
        )
        if not royal_canin_supplier:
            royal_canin_supplier = self.env["res.partner"].create(
                {"name": "Royal Canin", "supplier": True, "ref": "78650"}
            )

        # Assign the supplier royal canin to product 1
        self.product1.write(
            {
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": royal_canin_supplier.id,
                            "product_id": self.product1.id,
                            "product_tmpl_id": self.product1.product_tmpl_id.id,
                        },
                    )
                ]
            }
        )

        # Create the supplier Royal Canin if doesn't yet existing
        virbac_belgium_supplier = self.env["res.partner"].search(
            [("supplier", "=", True), ("ref", "=", "81200")]
        )
        if not virbac_belgium_supplier:
            virbac_belgium_supplier = self.env["res.partner"].create(
                {"name": "Virbac Belgium", "supplier": True, "ref": "81200"}
            )

        # Assign the supplier Virbac to product 2 ans set this product as food
        categ_diet = self.env.ref("specific_data.product_categ_ali_dietetique")
        self.product2.write(
            {
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": virbac_belgium_supplier.id,
                            "product_id": self.product2.id,
                            "product_tmpl_id": self.product2.product_tmpl_id.id,
                        },
                    )
                ],
                "categ_id": categ_diet.id,
            }
        )

        # Assign the supplier Virbac to product 3 and set this product as drug
        categ_pis = self.env.ref("specific_data.product_categ_pis")
        self.product3.write(
            {
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": virbac_belgium_supplier.id,
                            "product_id": self.product2.id,
                            "product_tmpl_id": self.product2.product_tmpl_id.id,
                        },
                    )
                ],
                "categ_id": categ_pis.id,
            }
        )

        backend = self.env["esb.backend"].get_singleton()
        skus = self.all_records.mapped("default_code")
        with backend.with_context(uid=olalux_user.id).work_on(
            "product.product"
        ) as work:
            component = work.component("ws.message.product.stock.sku")
            result = component.get_message(skus)

        product_mapper = {
            "Product1": self.product1,
            "Product2": self.product2,
            "Product3": self.product3,
        }

        self.assertEqual(len(result), 2)
        for product_values in result:
            product = product_mapper[product_values["sku"]]
            qty = product_values["quantity"]
            self.assertEqual(product.immediately_usable_qty, qty)
