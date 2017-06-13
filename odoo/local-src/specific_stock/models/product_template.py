# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date
from dateutil import relativedelta
import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    life_time = fields.Integer(
        related='categ_id.life_time',
    )

    use_time = fields.Integer(
        related='categ_id.use_time',
    )

    removal_time = fields.Integer(
        related='categ_id.removal_time',
    )

    alert_time = fields.Integer(
        related='categ_id.alert_time',
    )


# Due to a bug in odoo 10 we need to redefine the fields
class ProductProduct(models.Model):
    _inherit = 'product.product'

    life_time = fields.Integer(
        related='categ_id.life_time',
    )

    use_time = fields.Integer(
        related='categ_id.use_time',
    )

    removal_time = fields.Integer(
        related='categ_id.removal_time',
    )

    alert_time = fields.Integer(
        related='categ_id.alert_time',
    )

    date_last_inventory = fields.Datetime(
        'Last inventory',
        readonly=True)

    @api.model
    def get_products_daily_inventory(self):
        """
        This method will return a product.product browse record set
        with the daily inventory. The goal of the daily inventory is to
        inventory all products each 6 months
        or year (according the type of products).

        There are three type of products:
        - Expensive products (inventory each 6 months)
        - Best sellers products (inventory each 6 months)
        - Other products (inventory each year)
        :return:
        """
        config_param = self.env['ir.config_parameter']
        price = float(config_param
                      .get_param('stock.price_limit_for_inventory', 0))
        days = int(config_param.get_param('stock.nbr_open_days', 0))

        if not price or not days:
            raise UserError(_('Please set the Price limit for inventory '
                              'or/and the Number of open days '
                              'in the stock configuration'))

        product_ids = set()
        product_ids_to_ignore = set()

        # Expensive products
        # ------------------
        # An expensive product is a product where the price is greater or
        # equal to the "limit" price defined in the stock configuration.
        # We take products with the last inventory less than 6 months
        limite_date = date.today() - relativedelta.relativedelta(months=6)
        limite_date_str = fields.Date.to_string(limite_date)
        expensive_products = \
            self.search([('list_price', '>=', price),
                         '|',
                         ('date_last_inventory', '<', limite_date_str),
                         ('date_last_inventory', '=', False)])

        # Add all expensive products in the list to ignore
        product_ids_to_ignore.update(expensive_products.ids)

        qty_to_check = int(len(expensive_products) / days / 2)

        if qty_to_check >= len(expensive_products):
            product_ids.update(expensive_products.ids)
        else:
            product_sample_ids = \
                random.sample(expensive_products.ids, qty_to_check)
            product_ids.update(product_sample_ids)

        # Best sellers
        # ------------------
        # Products with an cost less than the limit price (see below)
        # ordered by the number of output.
        # We take only 20% (on the first part) to compute the qty to take.
        # On this part we'll take randomly n elements
        # rule: number of 20% best sellers / numbers of days / 2
        query = """
        SELECT line.product_id, count(*) AS cnt 
        FROM sale_order_line AS line
          INNER JOIN product_product AS product ON line.product_id = product.id
        WHERE (product.date_last_inventory < (NOW() - INTERVAL '6 months') 
          OR product.date_last_inventory IS NULL)
         AND line.create_date > (NOW() - INTERVAL '1 year')
         AND line.product_id NOT IN %s
        GROUP BY line.product_id 
        ORDER BY cnt DESC;
        """
        self.env.cr.execute(query, (tuple(product_ids_to_ignore), ))
        result = self.env.cr.fetchall()

        twenty_percent = int(len(result) * 0.2)

        best_sellers_ids = []
        for i in range(twenty_percent):
            best_sellers_ids.append(result[i][0])

        # Add best sellers in the list to ignore
        # These products doesn't take in count for the "others"
        product_ids_to_ignore.update(best_sellers_ids)

        qty_to_check = int(twenty_percent / days / 2)

        if qty_to_check >= twenty_percent:
            product_ids.update(best_sellers_ids)
        else:
            product_sample_ids = random.sample(best_sellers_ids,
                                               qty_to_check)
            product_ids.update(product_sample_ids)

        # Others
        # ------
        # Take all others products
        # (ignore all other products selected previously)
        # where the last inventory date is less than 6 months later
        query = """
        SELECT DISTINCT line.product_id
        FROM sale_order_line AS line
          INNER JOIN product_product AS product ON line.product_id = product.id
        WHERE (product.date_last_inventory < (NOW() - INTERVAL '1 year')
          OR product.date_last_inventory IS NULL)
         AND line.product_id NOT IN %s;
        """
        self.env.cr.execute(query, (tuple(product_ids_to_ignore),))
        result = self.env.cr.fetchall()

        other_product_ids = [x[0] for x in result]

        qty_to_check = int(len(other_product_ids) / days)

        if qty_to_check >= other_product_ids:
            product_ids.update(other_product_ids)
        else:
            product_sample_ids = random.sample(other_product_ids, qty_to_check)
            product_ids.update(product_sample_ids)

        return self.browse(product_ids)
