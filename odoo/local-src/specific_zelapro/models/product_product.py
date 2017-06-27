# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    year_ca = fields.Monetary('CA for 12 last months')
    year_ca_nbr_lines = fields.Integer('CA ')
    abc_id = fields.Many2one('activity.based.costing', string='ABC')

    @api.model
    def compute_ca_by_product(self):
        """
        Compute the CA for each products
        :return:
        """
        config_param = self.env['ir.config_parameter']
        ca_computation_delay = \
            int(config_param.get_param('zelapro.ca_computation_delay'))

        ca_by_products_query = """
        SELECT product_id, sum(price_subtotal), count(*)
        FROM account_invoice_line
        WHERE create_date > NOW() - INTERVAL '%s months'
        GROUP BY product_id;
        """ % ca_computation_delay
        self.env.cr.execute(ca_by_products_query)
        ca_by_products = {}
        for result in self.env.cr.fetchall():
            ca_by_products[result[0]] = (result[1], result[2])

        # Compute the CA for all products
        ca_total = 0.0
        products = self.env['product.product'].search([])
        for product in products:
            if product.id not in ca_by_products:
                year_ca = 0
                year_ca_nbr_lines = 0
            else:
                year_ca = ca_by_products[product.id][0]
                year_ca_nbr_lines = ca_by_products[product.id][1]

            product.write({
                'year_ca': year_ca,
                'year_ca_nbr_lines': year_ca_nbr_lines,
            })
            ca_total += year_ca

        return ca_total

    def compute_abc_rate(self, ca_total=0):
        """
        This method will compute the ABC rate for each products.
        For more information about the ABC method:
        https://en.wikipedia.org/wiki/Activity-based_costing

        The idea is to compute this rate according the CA
        of all products on one year (method compute_ca_by_product)

        The ABC method is computed according several rates.
        Normally there are three rates A, B and C
        For example, the rate A can be 80%. This rate will contain
        all products where the sum of all CA is less or equal
        than 80% of the glabel CA.
        :param ca_total: the global ca. Use only for test
        :return:
        """
        product_obj = self.env['product.product']

        abc_rates = self.env['activity.based.costing'].search([])
        abc_rates_lst = [(x.id, x.rate) for x in abc_rates]

        if not abc_rates_lst:
            raise UserError(_('Please define a least one ABC rate'))

        if not ca_total:
            ca_total = self.compute_ca_by_product()

        # Retrieve the first ABC rate
        current_abc_id, current_abc_rate = abc_rates_lst.pop(0)
        current_abc_total_amount = (ca_total / 100.0) * current_abc_rate
        current_abc_product_ids = []

        # Retrieve all products ordered by CA
        # If there is several products with the same CA they need to take
        # these products in one time
        ordered_product_ids_query = """
        SELECT year_ca, string_agg(id::TEXT, ',')
        FROM product_product
        WHERE active = TRUE
        GROUP BY year_ca
        ORDER BY year_ca DESC;
        """
        total_ca_amount = 0.0
        self.env.cr.execute(ordered_product_ids_query)
        product_ids_ordered_by_ca = self.env.cr.fetchall()
        while product_ids_ordered_by_ca:
            # If it is the last abc rate we don't need to compute the rest
            # We can stop the process here and set the current abc rate
            # to the rest of products.
            if not abc_rates_lst:
                product_remaining_ids = []
                for x in product_ids_ordered_by_ca:
                    product_remaining_ids += \
                        [int(y) for y in x[1].split(',')]

                products = product_obj.browse(product_remaining_ids)
                products.write({
                    'abc_id': current_abc_id
                })
                break

            # Pop the product CA and the list of products
            product_ca, product_ids_str = product_ids_ordered_by_ca.pop(0)
            product_ids = [int(y) for y in product_ids_str.split(',')]

            # Add these products ids in the list to update
            current_abc_product_ids += product_ids
            # Input the total CA amount
            total_ca_amount += product_ca * len(product_ids)

            # If the total CA amount is greater or equal than the total
            # amount of the current rate it means
            # that we need to the next rate.
            if total_ca_amount >= current_abc_total_amount:
                products = product_obj.browse(current_abc_product_ids)
                products.write({
                    'abc_id': current_abc_id,
                })

                # Switch to the next ABC rate and recompute the current rate
                current_abc_id, current_abc_rate = abc_rates_lst.pop(0)
                current_abc_total_amount = \
                    (ca_total / 100.0) * current_abc_rate
                current_abc_product_ids = []

                # If the new ABC rate is the last we continue the loop
                # We don't need to check the next ABC rate
                if not abc_rates_lst:
                    continue

                # We need to check the next ABC rate to be sure that
                # the next ABC rate is not lower than the current CA amount.
                # In some extremely rare case a ABC rate can be skipped
                # Eg:
                # Rate A: 40€
                # Rate B: 70€
                # Rate C: 100€
                # We have two products (Product 1 with total CA to 75€
                # and product 2 with total CA to 10€)
                # The product 1 should have the rate A and the product 2
                # should have the rate C (and not B !!!)
                next_abc_id, next_abc_rate = abc_rates_lst[0]
                next_abc_total_amount = \
                    (ca_total / 100.0) * next_abc_rate
                while next_abc_total_amount < total_ca_amount:
                    current_abc_id, current_abc_rate = abc_rates_lst.pop(0)
                    current_abc_total_amount = \
                        (ca_total / 100.0) * current_abc_rate
                    current_abc_product_ids = []

                    if abc_rates_lst:
                        next_abc_id, next_abc_rate = abc_rates_lst[0]
                        next_abc_total_amount = \
                            (ca_total / 100.0) * next_abc_rate
