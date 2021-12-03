# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date, datetime as dt

from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import TransactionCase


class TestStockInventory(TransactionCase):
    post_install = True
    at_install = False

    def test_date_last_inventory(self):
        """
        Check if the date of the last inventory
        is correctly change when we do an inventory.
        The last inventory date should not change
        when we update the quantity on hand
        :return:
        """
        product = self.env["product.product"].create(
            {"name": "Unittest P1", "uom_id": self.ref("product.product_uom_unit")}
        )
        self.assertFalse(product.date_last_inventory)

        inventory = self.env["stock.inventory"].create(
            {"name": "Test date last inventory", "filter": "product"}
        )
        inventory_line = inventory.line_ids.create(
            {
                "inventory_id": inventory.id,
                "product_id": product.id,
                "product_qty": 20,
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        # Validate the inventory
        inventory.action_done()

        # The date_last_inventory date is set to "NOW".
        # It should be the same date than the create date of the line.
        # However, sometime the date_last_inventory date is not really
        # the same than the create date of the line.
        # It's why I check that the date_last_inventory is greater or equal
        # to the create_date of the line.
        self.assertGreaterEqual(product.date_last_inventory, inventory_line.create_date)
        current_date_last_inventory = product.date_last_inventory

        # Now we wil update the quantity on hand with the wizard
        # The date_last_inventory should not change
        wizard_obj = self.env["stock.change.product.qty"]
        update_qty_wizard = wizard_obj.create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": 16,
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        update_qty_wizard.change_product_qty()

        self.assertEqual(product.date_last_inventory, current_date_last_inventory)

    def test_create_daily_inventory(self):
        """
        Test if the method test_create_daily_inventory skip all weekends days
        and bank holidays.
        :return:
        """
        config_param = self.env["ir.config_parameter"]
        config_param.set_param("stock.price_limit_for_inventory", 100)
        config_param.set_param("stock.nbr_open_days", 220)

        date_test = date(2017, 1, 31)
        self.env["bank.holiday"].create(
            {"name": "Test", "date": fields.Date.to_string(date_test)}
        )

        inventory = self.env["stock.inventory"].create_daily_inventory(
            date_today_overwrite=date_test
        )
        self.assertIsNone(inventory)

        # 1 january is a Sunday
        date_test = date(2017, 1, 1)
        inventory = self.env["stock.inventory"].create_daily_inventory(
            date_today_overwrite=date_test
        )
        self.assertIsNone(inventory)

    def test_compute_inventory_periods(self):
        company = self.env.user.company_id
        company.write({"fiscalyear_last_month": 12, "fiscalyear_last_day": 31})

        ir_config = self.env["ir.config_parameter"]
        ir_config.set_param("stock.delay_inventory_expensive_products", 6)
        ir_config.set_param("stock.delay_inventory_best_sellers_products", 2)
        ir_config.set_param("stock.delay_inventory_other_products", 12)

        date_today = date.today()
        date_july = date_today.replace(month=7)
        result = self.env["stock.inventory"].compute_inventory_periods(date_july)

        self.assertEqual(len(result), 3)

        # Delay of 6 months
        expensive_products = result["expensive"]
        self.assertEqual(expensive_products["date_start"], "%s-07-01" % date_today.year)
        self.assertEqual(expensive_products["date_end"], "%s-12-31" % date_today.year)
        self.assertEqual(expensive_products["delay"], 6)
        self.assertEqual(expensive_products["nbr_inventory_per_year"], 2)

        # Delay of 2 months
        best_sellers_products = result["best_sellers"]
        self.assertEqual(
            best_sellers_products["date_start"], "%s-07-01" % date_today.year
        )
        self.assertEqual(
            best_sellers_products["date_end"], "%s-08-31" % date_today.year
        )
        self.assertEqual(best_sellers_products["delay"], 2)
        self.assertEqual(best_sellers_products["nbr_inventory_per_year"], 6)

        # Delay of 12 months
        other_products = result["other"]
        self.assertEqual(other_products["date_start"], "%s-01-01" % date_today.year)
        self.assertEqual(other_products["date_end"], "%s-12-31" % date_today.year)
        self.assertEqual(other_products["delay"], 12)
        self.assertEqual(other_products["nbr_inventory_per_year"], 1)

    # pylint: disable=no-self-argument
    @freeze_time("2018-06-01", as_arg=True)
    def test_get_products_daily_inventory(frozen_time, self):
        """
        To test the method get_products_daily_inventory we need to create a
        subset of products.
        This this will create following products:
        - 2 expensive products (with a price greater than 5000)
        - 10 products with sales orders
        :return:
        """
        # Change the fiscal year to have a year from 1 january to 31 december
        company = self.env.user.company_id
        company.write({"fiscalyear_last_month": 12, "fiscalyear_last_day": 31})

        product_obj = self.env["product.product"]
        so_obj = self.env["sale.order"]
        stock_obj = self.env["stock.inventory"]
        uom_id = self.ref("product.product_uom_unit")

        partner = self.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "92837498234"}
        )

        ir_config = self.env["ir.config_parameter"]
        ir_config.set_param("stock.price_limit_for_inventory", 5000)
        ir_config.set_param("stock.nbr_open_days", 2)
        ir_config.set_param("stock.delay_inventory_expensive_products", 6)
        ir_config.set_param("stock.delay_inventory_best_sellers_products", 6)
        ir_config.set_param("stock.delay_inventory_other_products", 12)
        ir_config.set_param("stock.months_between_inventory", 2)
        ir_config.set_param("stock.best_sellers_duration", 12)

        # Disable all products to take only new products in count
        update_date_last_inventory_query = """
        UPDATE product_product SET active = FALSE;
        """
        self.env.cr.execute(update_date_last_inventory_query)

        # Create products (12 products)
        #######################
        # - The product 1 has two SO
        # - The product 2 has three SO
        # - The product 4 and 8 are an expensive product (> 5K)
        default_price = 1000
        product_prices = {"product_4": 10000, "product_7": 15000}

        default_nbr_of_so = 1
        nbr_of_so = {"product_1": 2, "product_2": 3}

        for i in range(1, 13):
            # Create the product
            product_name = "product_%s" % i
            product = product_obj.create(
                {
                    "name": product_name,
                    "uom_id": uom_id,
                    "list_price": product_prices.get(product_name, default_price),
                    "type": "product",
                }
            )
            setattr(self, product_name, product)

            # Create sale orders
            number_of_so = nbr_of_so.get(product_name, default_nbr_of_so)
            for _x in range(number_of_so):
                so_obj.create(
                    {
                        "partner_id": partner.id,
                        "order_line": [
                            (
                                0,
                                0,
                                {
                                    "name": "Line for SO",
                                    "product_id": product.id,
                                    "product_uom": uom_id,
                                    "product_uom_qty": 10,
                                    "sequence": 1,
                                },
                            )
                        ],
                    }
                )

        # Create a first inventory
        assert dt.now() == dt(2018, 6, 1)
        self.env["bank.holiday"].search([("date", "=", fields.Date.today())]).unlink()

        inventory = stock_obj.create_daily_inventory()
        inventory.prepare_inventory()
        inventory_products = inventory.line_ids.mapped("product_id")

        # I must have 8 products in this inventory
        # - 2 expensive product
        #       nbr of expensive products / (days / nbr inv per year)
        #       2 / (2 / 2) = 1 product
        # - 2 best seller
        #       nbr of best sellers / (days / nbr inv per year)
        #       2 / (2 / 2) = 2 products
        # - 4 other products
        #       nbr of products / (days / nbr inv per year)
        #       8 products left / (2 / 1) = 4 products
        self.assertEqual(len(inventory_products), 8)

        # Check if all expensive products are in the inventory
        self.assertTrue(
            self.product_7 in inventory_products
            and self.product_4 in inventory_products
        )

        # Check if all best sellers products are in the inventory
        self.assertTrue(
            self.product_1 in inventory_products
            and self.product_2 in inventory_products
        )

        # Validate the inventory
        inventory.action_done()

        # Rewrite the last_inventory_date
        inventory_products.write({"date_last_inventory": fields.Date.today()})

        # Create a inventory the next day month
        frozen_time.move_to("2018-07-20")
        assert dt.now() == dt(2018, 7, 20)
        self.env["bank.holiday"].search([("date", "=", fields.Date.today())]).unlink()

        inventory = stock_obj.create_daily_inventory()
        inventory_products = inventory.product_ids

        # This inventory will contains 4 products
        # - 0 expensive products
        # - 0 best sellers products
        # - 4 other products
        # We have no expensive products and best sellers because
        # we want two months between two inventory.
        self.assertEqual(len(inventory_products), 4)

        # We'll not validate this inventory and create a new one
        # I'll change the duration between two inventory
        ir_config.set_param("stock.months_between_inventory", "1")

        inventory = stock_obj.create_daily_inventory()
        inventory_products = inventory.product_ids
        # This inventory will contains 8 products
        # - 2 expensive product
        # - 2 best seller
        # - 4 other products
        self.assertEqual(len(inventory_products), 8)
