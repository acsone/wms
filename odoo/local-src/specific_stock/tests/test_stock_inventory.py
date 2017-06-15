# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

from odoo import fields
from odoo.tests.common import TransactionCase, post_install, at_install


class TestStockInventory(TransactionCase):

    @post_install(True)
    @at_install(False)
    def test_date_last_inventory(self):
        """
        Check if the date of the last inventory
        is correctly change when we do an inventory.
        The last inventory date should not change
        when we update the quantity on hand
        :return:
        """
        product = self.env['product.product'].create({
            'name': 'Unittest P1',
            'uom_id': self.ref('product.product_uom_unit'),
        })
        self.assertFalse(product.date_last_inventory)

        inventory = self.env['stock.inventory'].create({
            'name': 'Test date last inventory',
            'filter': 'product',
        })
        inventory_line = inventory.line_ids.create({
            'inventory_id': inventory.id,
            'product_id': product.id,
            'product_qty': 20,
            'location_id': self.env.ref('stock.stock_location_stock').id
        })
        # Validate the inventory
        inventory.action_done()

        # The date_last_inventory date is set to "NOW".
        # It should be the same date than the create date of the line.
        # However, sometime the date_last_inventory date is not really
        # the same than the create date of the line.
        # It's why I check that the date_last_inventory is greater or equal
        # to the create_date of the line.
        self.assertTrue(
            product.date_last_inventory >= inventory_line.create_date
        )
        current_date_last_inventory = product.date_last_inventory

        # Now we wil update the quantity on hand with the wizard
        # The date_last_inventory should not change
        wizard_obj = self.env['stock.change.product.qty']
        update_qty_wizard = wizard_obj.create({
            'product_id': product.id,
            'product_tmpl_id': product.product_tmpl_id.id,
            'new_quantity': 16,
            'location_id': self.env.ref('stock.stock_location_stock').id,
        })
        update_qty_wizard.change_product_qty()

        self.assertEqual(product.date_last_inventory,
                         current_date_last_inventory)

    @post_install(True)
    @at_install(False)
    def test_compute_inventory_periods(self):
        company = self.env.user.company_id
        company.write({
            'fiscalyear_last_month': 12,
            'fiscalyear_last_day': 31,
        })

        ir_config = self.env['ir.config_parameter']
        ir_config.set_param('stock.delay_inventory_expensive_products', 6)
        ir_config.set_param('stock.delay_inventory_best_sellers_products', 2)
        ir_config.set_param('stock.delay_inventory_other_products', 12)

        date_today = date.today()
        date_july = date_today.replace(month=7)
        result = self.env['stock.inventory']\
            .compute_inventory_periods(date_july)

        self.assertEqual(len(result), 3)

        # Delay of 6 months
        expensive_products = result['expensive']
        self.assertEqual(expensive_products['date_start'],
                         '%s-07-01' % date_today.year)
        self.assertEqual(expensive_products['date_end'],
                         '%s-12-31' % date_today.year)
        self.assertEqual(expensive_products['delay'], 6)
        self.assertEqual(expensive_products['nbr_inventory_per_year'], 2)

        # Delay of 2 months
        best_sellers_products = result['best_sellers']
        self.assertEqual(best_sellers_products['date_start'],
                         '%s-07-01' % date_today.year)
        self.assertEqual(best_sellers_products['date_end'],
                         '%s-08-31' % date_today.year)
        self.assertEqual(best_sellers_products['delay'], 2)
        self.assertEqual(best_sellers_products['nbr_inventory_per_year'], 6)

        # Delay of 12 months
        other_products = result['other']
        self.assertEqual(other_products['date_start'],
                         '%s-01-01' % date_today.year)
        self.assertEqual(other_products['date_end'],
                         '%s-12-31' % date_today.year)
        self.assertEqual(other_products['delay'], 12)
        self.assertEqual(other_products['nbr_inventory_per_year'], 1)

    @post_install(True)
    @at_install(False)
    def test_get_products_daily_inventory(self):
        """
        To test the method get_products_daily_inventory we need to create a
        subset of products.
        This this will create following products:
        - 2 expensive products (with a price greater than 5000)
        - 10 products with sales orders
        :return:
        """
        product = self.env['product.product']
        uom_id = self.ref('product.product_uom_unit')

        partner = self.env['res.partner'].create({
            'name': 'Unittest partner',
        })

        ir_config = self.env['ir.config_parameter']
        ir_config.set_param('stock.price_limit_for_inventory', 5000)
        ir_config.set_param('stock.nbr_open_days', 2)
        ir_config.set_param('stock.delay_inventory_expensive_products', 6)
        ir_config.set_param('stock.delay_inventory_best_sellers_products', 6)
        ir_config.set_param('stock.delay_inventory_other_products', 12)
        ir_config.set_param('stock.months_between_inventory', 2)

        # I need to set a date_last_inventory to all products
        # to ignore existing products during tests
        update_date_last_inventory_query = """
        UPDATE product_product SET date_last_inventory = NOW();
        """
        self.env.cr.execute(update_date_last_inventory_query)

        # Create products (12 products)
        #######################
        # The best seller 1 has 2 sales orders
        # The best seller 2 has 3 sales orders
        # Two products with price greater than 5000
        product_1_sec_best_seller = product.create({
            'name': 'Product 1 (seconde best seller)',
            'uom_id': uom_id,
            'list_price': 3000
        })
        product_2_best_seller = product.create({
            'name': 'Product 2 (best seller)',
            'uom_id': uom_id,
            'list_price': 1000
        })
        product_3 = product.create({
            'name': 'Product 3',
            'uom_id': uom_id,
            'list_price': 1000
        })
        product_4_sec_expensive = product.create({
            'name': 'Product 4 (second expensive product)',
            'uom_id': uom_id,
            'list_price': 10000
        })
        product_5 = product.create({
            'name': 'Product 5',
            'uom_id': uom_id,
            'list_price': 1000
        })
        product_6 = product.create({
            'name': 'Product 6',
            'uom_id': uom_id,
            'list_price': 1000
        })
        product_7_most_expensive = product.create({
            'name': 'Product 7 (most expensive)',
            'uom_id': uom_id,
            'list_price': 15000
        })
        product_8 = product.create({
            'name': 'Product 8',
            'uom_id': uom_id,
            'list_price': 1000
        })
        product_9 = product.create({
            'name': 'Product 9',
            'uom_id': uom_id,
            'list_price': 1000
        })
        product_10 = product.create({
            'name': 'Product 10',
            'uom_id': uom_id,
            'list_price': 1000
        })
        product_11 = product.create({
            'name': 'Product 11',
            'uom_id': uom_id,
            'list_price': 1000
        })
        product_12 = product.create({
            'name': 'Product 12',
            'uom_id': uom_id,
            'list_price': 1000
        })

        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 1',
                    'product_id': product_1_sec_best_seller.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 1',
                    'product_id': product_1_sec_best_seller.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 2',
                    'product_id': product_2_best_seller.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 2',
                    'product_id': product_2_best_seller.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 2',
                    'product_id': product_2_best_seller.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 3',
                    'product_id': product_3.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 4',
                    'product_id': product_4_sec_expensive.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 5',
                    'product_id': product_5.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 6',
                    'product_id': product_6.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 7',
                    'product_id': product_7_most_expensive.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 8',
                    'product_id': product_8.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 9',
                    'product_id': product_9.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 10',
                    'product_id': product_10.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 11',
                    'product_id': product_11.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })
        self.env['sale.order'].create({
            'partner_id': partner.id,
            'order_line': [
                (0, 0, {
                    'name': 'Product 12',
                    'product_id': product_12.id,
                    'product_uom': uom_id,
                    'product_uom_qty': 10,
                    'sequence': 1,
                }),
            ]
        })

        # Create a first inventory
        date_today_overwrite = date(year=2017, month=1, day=1)
        periods = {
            'expensive': {
                'date_start': '2017-01-01',
                'date_end': '2017-01-01',
                'delay': 6,
                'nbr_inventory_per_year': 2,
            },
            'best_sellers': {
                'date_start': '2017-01-01',
                'date_end': '2017-01-01',
                'delay': 6,
                'nbr_inventory_per_year': 2,
            },
            'other': {
                'date_start': '2017-01-01',
                'date_end': '2017-01-02',
                'delay': 12,
                'nbr_inventory_per_year': 1,
            },
        }
        inventory_products = product.get_products_daily_inventory(
            periods, date_today_overwrite=date_today_overwrite
        )

        # I must have 8 products in this inventory
        # - 2 expensive product
        #       nbr of expensive products / (days / nbr inv per year)
        #       2 / (2 / 2) = 1 product
        # - 2 best seller
        #       20% of nbr of products with so / (days / nbr inv per year)
        #       20% of 10 / (2 / 2) = 2 products
        # - 4 other products
        #       nbr of products / (days / nbr inv per year)
        #       8 products left / (2 / 1) = 4 products
        self.assertEqual(len(inventory_products), 8)

        # Check if one of the two most expensive product is in the inventory
        self.assertTrue(product_7_most_expensive in inventory_products
                        and product_4_sec_expensive in inventory_products)

        # One of the two best sellers should be in the inventory
        self.assertTrue(product_2_best_seller in inventory_products
                        and product_1_sec_best_seller in inventory_products)

        inventory = self.env['stock.inventory'].create({
            'name': 'Daily inventory: %s' % fields.Date.today(),
            'filter': 'partial',
        })

        location_id = self.env.ref('stock.stock_location_stock').id
        for product in inventory_products:
            inventory.line_ids.create({
                'inventory_id': inventory.id,
                'product_id': product.id,
                'product_qty': 20,
                'location_id': location_id
            })

        # Validate the inventory
        inventory.action_done()
        # The method action_done will write the date_last_inventory with today
        # or the real date_last_inventory should be 2017-01-01
        inventory_products.write({
            'date_last_inventory': '2017-01-01'
        })

        # Create a first inventory
        date_today_overwrite = date(year=2017, month=1, day=2)
        new_periods = {
            'expensive': {
                'date_start': '2017-01-02',
                'date_end': '2017-01-02',
                'delay': 6,
                'nbr_inventory_per_year': 2,
            },
            'best_sellers': {
                'date_start': '2017-01-02',
                'date_end': '2017-01-02',
                'delay': 6,
                'nbr_inventory_per_year': 2,
            },
            'other': {
                'date_start': '2017-01-01',
                'date_end': '2017-01-02',
                'delay': 12,
                'nbr_inventory_per_year': 1,
            },
        }
        new_inventory_products = product.get_products_daily_inventory(
            new_periods, date_today_overwrite=date_today_overwrite
        )
        # I must have 4 products in this inventory
        # - 0 expensive product
        # - 0 best seller
        # - 4 other products
        #       nbr of products / (days / nbr inv per year)
        #       8 products left / (2 / 1) = 4 products
        self.assertEqual(len(new_inventory_products), 4)

        # We'll not validate this inventory and create a new one
        ir_config.set_param('stock.months_between_inventory', '0')

        new_inventory_products = product.get_products_daily_inventory(
            new_periods, date_today_overwrite=date_today_overwrite
        )
        # I must have 4 products in this inventory
        # - 2 expensive product
        # - 2 best seller
        # - 4 other products
        #       nbr of products / (days / nbr inv per year)
        #       8 products left / (2 / 1) = 4 products
        self.assertEqual(len(new_inventory_products), 8)
