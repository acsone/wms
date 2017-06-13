# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
    def test_get_products_daily_inventory(self):
        """
        To test the method get_products_daily_inventory we need to create a
        subset of products.
        This this will create following products:
        - 2 expensive products (with a price greater than 5000)
        - 10 products with sales orders
        :return:
        """
        config_param = self.env['ir.config_parameter']
        product = self.env['product.product']
        uom_id = self.ref('product.product_uom_unit')

        partner = self.env['res.partner'].create({
            'name': 'Unittest partner',
        })

        config_param.set_param('stock.price_limit_for_inventory', 5000)
        config_param.set_param('stock.nbr_open_days', 1)

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
        inventory_products = product.get_products_daily_inventory()

        # I must have 6 products in this inventory
        # - 1 expensive product (nbr of expensive products / days / 2)
        #       2 / 1 / 2 = 1 product
        # - 1 best seller (20% of nbr of products with so / days / 2)
        #       20% of 10 / 1 / 2 = 1 products
        # - 8 other products (nbr of products / days)
        #       8 products left / 1 = 8 products
        self.assertEqual(len(inventory_products), 10)

        # Check if one of the two most expensive product is in the inventory
        self.assertTrue(product_7_most_expensive in inventory_products
                        or product_4_sec_expensive in inventory_products)

        # One of the two best sellers should be in the inventory
        self.assertTrue(product_2_best_seller in inventory_products
                        or product_1_sec_best_seller in inventory_products)

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

        # Create a new inventory
        new_inventory_products = product.get_products_daily_inventory()

        # I should have
        # - 0 expensive product (1 product left but 1 divided by 2 = 0.5)
        # - 0 best seller (20% of 1 product divided by 2 = 0.1)
        # - 1 other product
        # Why only 1 product ?
        # In the first inventory we take 1 expensive product, 1 best seller
        # and 8 other products => 10 products
        # After that I've two products without inventory
        # (1 expensive product and 1 simple product)
        # I cannot take the last expensive product and a best seller
        # (due to the split). I still have a product
        self.assertEqual(len(new_inventory_products), 1)
