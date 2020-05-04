# -*- coding: utf-8 -*-
# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common


class TestCodeABC(common.TransactionCase):
    def test_business_unit_id(self):
        product_category = self.env["product.category"]
        business_unit = product_category.create(
            {"name": "Business Unit", "is_business_unit": True}
        )

        sub_category = product_category.create(
            {"name": "Test", "parent_id": business_unit.id}
        )

        product = self.env["product.product"].create(
            {"name": "Product", "categ_id": sub_category.id}
        )
        self.assertEquals(product.business_unit_id, business_unit)

    def test_compute_turnover_by_product(self):
        """
        Compute the turnover for all products and check the sum
        :return:
        """

        disable_products = "UPDATE product_product SET active = FALSE;"
        self.env.cr.execute(disable_products)

        product_obj = self.env["product.product"]
        invoice_obj = self.env["account.invoice"]

        journal = invoice_obj._default_journal()
        account_type_rec = self.env.ref("account.data_account_type_receivable")
        account = self.env["account.account"].create(
            {
                "code": "400001",
                "name": "Clients (test)",
                "user_type_id": account_type_rec.id,
                "reconcile": True,
            }
        )

        tag_operation = self.env.ref("account.account_tag_operating")
        account_type_inc = self.env.ref("account.data_account_type_revenue")
        account_line = self.env["account.account"].create(
            {
                "code": "701001",
                "name": "Ventes en Belgique (test)",
                "user_type_id": account_type_inc.id,
                "reconcile": True,
                "tag_ids": [(6, 0, [tag_operation.id])],
            }
        )

        partner = self.env["res.partner"].create({"name": "Partner", "ref": "12312394"})

        business_unit = self.env["product.category"].create(
            {"name": "Business Unit", "is_business_unit": True}
        )

        ir_config = self.env["ir.config_parameter"]
        ir_config.set_param("abc.turnover_delay", 12)

        # The product 5 doesn't have invoices. The turnover for this product
        # is equal to 0 and the ABC code must be empty !!!
        invoices_by_product = {
            1: (1, 100),  # turnover 100
            2: (2, 25),  # turnover 50
            3: (8, 10),  # turnover 80
            4: (15, 20),  # turnover 300
            5: (0, 0),  # turnover 0,
            6: (1, 50),  # turnover 50
            7: (16, 5),  # turnover 80
            8: (5, 20),  # turnover 100
            9: (25, 8),  # turnover 200
            10: (8, 5),  # turnover 40
        }

        # Create all products (see invoices_by_product)
        for product_num in range(1, len(invoices_by_product) + 1):
            product = product_obj.create(
                {"name": "Product %s" % product_num, "categ_id": business_unit.id}
            )
            setattr(self, "product_%s" % product_num, product)

            quantity, price_unit = invoices_by_product[product_num]
            invoice_obj.create(
                {
                    "partner_id": partner.id,
                    "journal_id": journal.id,
                    "account_id": account.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": product.id,
                                "name": "Invoice Line %s" % product_num,
                                "account_id": account_line.id,
                                "quantity": quantity,
                                "price_unit": price_unit,
                            },
                        )
                    ],
                }
            )

        product_obj.compute_turnover_by_product()

        self.assertEquals(getattr(self, "product_1").turnover, 100.0)
        self.assertEquals(getattr(self, "product_2").turnover, 50.0)
        self.assertEquals(getattr(self, "product_3").turnover, 80.0)
        self.assertEquals(getattr(self, "product_4").turnover, 300.0)
        self.assertEquals(getattr(self, "product_5").turnover, 0.0)

        self.assertEquals(getattr(self, "product_6").turnover_nbr_lines, 1)
        self.assertEquals(getattr(self, "product_7").turnover_nbr_lines, 1)

        # Create ABC rate
        abc_obj = self.env["code.abc"]
        abc_obj.search([]).unlink()
        rate_a = abc_obj.create({"code": "A", "rate": 60})
        rate_b = abc_obj.create({"code": "B", "rate": 75})
        rate_c = abc_obj.create({"code": "C", "rate": 100})

        product_obj.compute_abc_rate()

        self.assertEqual(getattr(self, "product_1").abc_id, rate_a)
        self.assertEqual(getattr(self, "product_2").abc_id, rate_c)
        self.assertEqual(getattr(self, "product_3").abc_id, rate_b)
        self.assertEqual(getattr(self, "product_4").abc_id, rate_a)
        self.assertEqual(getattr(self, "product_5").abc_id, abc_obj)
        self.assertEqual(getattr(self, "product_6").abc_id, rate_c)
        self.assertEqual(getattr(self, "product_7").abc_id, rate_b)
        self.assertEqual(getattr(self, "product_8").abc_id, rate_a)
        self.assertEqual(getattr(self, "product_9").abc_id, rate_a)
        self.assertEqual(getattr(self, "product_10").abc_id, rate_c)

    def test_multiple_business_unit(self):
        """
        Compute the ABC code with several business unit
        Product 1, 2 and 3 are in the business unit 1 (turnover 200€)
        Product 4 and 5 are in the business unit 2 (turnover 100€)
        :return:
        """

        disable_products = "UPDATE product_product SET active = FALSE;"
        self.env.cr.execute(disable_products)

        product_obj = self.env["product.product"]
        invoice_obj = self.env["account.invoice"]

        journal = invoice_obj._default_journal()
        account_type_rec = self.env.ref("account.data_account_type_receivable")
        account = self.env["account.account"].create(
            {
                "code": "400001",
                "name": "Clients (test)",
                "user_type_id": account_type_rec.id,
                "reconcile": True,
            }
        )

        tag_operation = self.env.ref("account.account_tag_operating")
        account_type_inc = self.env.ref("account.data_account_type_revenue")
        account_line = self.env["account.account"].create(
            {
                "code": "701001",
                "name": "Ventes en Belgique (test)",
                "user_type_id": account_type_inc.id,
                "reconcile": True,
                "tag_ids": [(6, 0, [tag_operation.id])],
            }
        )

        partner = self.env["res.partner"].create({"name": "Partner", "ref": "87564334"})

        business_unit_1 = self.env["product.category"].create(
            {"name": "Business Unit 1", "is_business_unit": True}
        )

        business_unit_2 = self.env["product.category"].create(
            {"name": "Business Unit 2", "is_business_unit": True}
        )

        ir_config = self.env["ir.config_parameter"]
        ir_config.set_param("abc.turnover_delay", 12)

        # BU 1: turnover 200
        # BU 2: turnover 100
        invoices_by_product = {
            1: (business_unit_1.id, 1, 140),  # BU1 - turnover 140
            2: (business_unit_1.id, 4, 10),  # BU1 - turnover 40
            3: (business_unit_1.id, 2, 10),  # BU1 - turnover 20
            4: (business_unit_2.id, 3, 25),  # BU2 - turnover 75
            5: (business_unit_2.id, 2, 12.5),  # BU2 - turnover 25,
        }

        # Create all products (see invoices_by_product)
        for product_num in range(1, len(invoices_by_product) + 1):
            categ_id, quantity, price_unit = invoices_by_product[product_num]
            product = product_obj.create(
                {"name": "Product %s" % product_num, "categ_id": categ_id}
            )
            setattr(self, "product_%s" % product_num, product)

            invoice_obj.create(
                {
                    "partner_id": partner.id,
                    "journal_id": journal.id,
                    "account_id": account.id,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "product_id": product.id,
                                "name": "Invoice Line %s" % product_num,
                                "account_id": account_line.id,
                                "quantity": quantity,
                                "price_unit": price_unit,
                            },
                        )
                    ],
                }
            )

        product_obj.compute_turnover_by_product()

        self.assertEquals(float(business_unit_1.turnover), 200)
        self.assertEquals(float(business_unit_2.turnover), 100)

        # Create ABC rate
        abc_obj = self.env["code.abc"]
        abc_obj.search([]).unlink()
        rate_a = abc_obj.create({"code": "A", "rate": 60})
        rate_b = abc_obj.create({"code": "B", "rate": 75})
        rate_c = abc_obj.create({"code": "C", "rate": 100})

        product_obj.compute_abc_rate()

        self.assertEqual(getattr(self, "product_1").abc_id, rate_a)
        self.assertEqual(getattr(self, "product_2").abc_id, rate_b)
        self.assertEqual(getattr(self, "product_3").abc_id, rate_c)
        self.assertEqual(getattr(self, "product_4").abc_id, rate_a)
        self.assertEqual(getattr(self, "product_5").abc_id, rate_c)
