# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date
from dateutil.relativedelta import relativedelta
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
    def get_products_daily_inventory(self,
                                     inventory_periods,
                                     date_today_overwrite=None):
        """
        This method will return a product.product browse record set
        with the daily inventory. The goal of the daily inventory is to
        inventory all products according the product type delay.

        There are three type of products:
        - Expensive products
        - Best sellers products
        - Other products

        For each product type we will compute the number of products
        to inventory.
        Here is the formula for computing the number of products per day.

        nbr of products in the category to be inventoried /
        (nbr of open days in the year / nbr of inventory per year)

        Information: If we are in the last day of the period we don't divide
        by the number of days in the year and nbr of inventory per year.
        :return:
        """
        config_param = self.env['ir.config_parameter']
        price = float(config_param
                      .get_param('stock.price_limit_for_inventory', 0))
        days = int(config_param.get_param('stock.nbr_open_days', 0))
        interval_between_inventory = int(
            config_param.get_param('stock.months_between_inventory', 0)
        )
        date_today = date_today_overwrite or date.today()
        maximum_last_inventory_date = \
            date_today - relativedelta(months=interval_between_inventory)
        maximum_last_inventory_date_str = \
            fields.Date.to_string(maximum_last_inventory_date)

        if not price or not days:
            raise UserError(_('Please set the Price limit for inventory '
                              'or/and the Number of open days '
                              'in the stock configuration'))

        product_ids = set()
        # SQL doesn't like when where where clause contains a "NOT IN ()"
        # To avoid to do a lot of tricks to avoid this I add a zero in the list
        # There are no ID zero in DB.
        product_ids_to_ignore = set([0])

        # Expensive products
        # ------------------
        # An expensive product is a product where the price is greater or
        # equal to the "limit" price defined in the stock configuration.
        expensive_period = inventory_periods.get('expensive')
        if not expensive_period:
            raise UserError(_('There is no period for expensive products'))
        expensive_period_start = expensive_period['date_start']
        expensive_period_end = expensive_period['date_end']
        expensive_period_nbr_year = expensive_period['nbr_inventory_per_year']

        if maximum_last_inventory_date_str < expensive_period_start:
            expensive_period_start = maximum_last_inventory_date_str

        query = """
        SELECT product.id
        FROM product_product AS product
          INNER JOIN product_template AS template 
            ON product.product_tmpl_id = template.id
        WHERE template.list_price >= %s
        AND (product.date_last_inventory < %s
             OR product.date_last_inventory IS NULL);
        """
        query_args = [price, expensive_period_start]

        self.env.cr.execute(query, tuple(query_args))
        result = self.env.cr.fetchall()
        expensive_products_ids = [x[0] for x in result]

        # Add all expensive products in the list to ignore
        product_ids_to_ignore.update(expensive_products_ids)

        if expensive_period_end == fields.Date.to_string(date_today):
            qty_to_check = len(expensive_period_end)
        else:
            qty_to_check = int(len(expensive_products_ids) /
                               (days / expensive_period_nbr_year))

        if qty_to_check >= len(expensive_products_ids):
            product_ids.update(expensive_products_ids)
        else:
            product_sample_ids = \
                random.sample(expensive_products_ids, qty_to_check)
            product_ids.update(product_sample_ids)

        # Best sellers
        # ------------------
        # Products with a cost less than the limit price (see below)
        # ordered by the number of output.
        # We take only 20% (on the first part) to compute the qty to take.
        best_sellers_period = inventory_periods.get('best_sellers')
        if not best_sellers_period:
            raise UserError(_('There is no period for best sellers products'))
        best_sellers_period_start = best_sellers_period['date_start']
        best_sellers_period_end = best_sellers_period['date_end']
        best_sellers_period_nbr_year = \
            best_sellers_period['nbr_inventory_per_year']

        if maximum_last_inventory_date_str < best_sellers_period_start:
            best_sellers_period_start = maximum_last_inventory_date_str

        query = """
        SELECT line.product_id, count(*) AS cnt
        FROM sale_order_line AS line
          INNER JOIN product_product AS product ON line.product_id = product.id
        WHERE line.create_date > (NOW() - INTERVAL '1 year')
         AND line.product_id NOT IN %s
         AND (product.date_last_inventory < %s
              OR product.date_last_inventory IS NULL)
        GROUP BY line.product_id
        ORDER BY cnt DESC;
        """
        query_args = [tuple(product_ids_to_ignore), best_sellers_period_start]

        self.env.cr.execute(query, tuple(query_args))
        result = self.env.cr.fetchall()

        twenty_percent = int(len(result) * 0.2)

        best_sellers_ids = []
        for i in range(twenty_percent):
            best_sellers_ids.append(result[i][0])

        # Add best sellers in the list to ignore
        # These products doesn't take in count for the "others"
        product_ids_to_ignore.update(best_sellers_ids)

        if best_sellers_period_end == fields.Date.to_string(date_today):
            qty_to_check = len(best_sellers_period_end)
        else:
            qty_to_check = int(twenty_percent /
                               (days / best_sellers_period_nbr_year))

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
        other_period = inventory_periods.get('other')
        if not other_period:
            raise UserError(_('There is no period for other products'))
        other_period_start = other_period['date_start']
        other_period_end = other_period['date_end']
        other_period_nbr_year = other_period['nbr_inventory_per_year']

        if maximum_last_inventory_date_str < other_period_start:
            other_period_start = maximum_last_inventory_date_str

        query = """
        SELECT DISTINCT line.product_id
        FROM sale_order_line AS line
          INNER JOIN product_product AS product ON line.product_id = product.id
        WHERE line.product_id NOT IN %s
         AND (product.date_last_inventory < %s
              OR product.date_last_inventory IS NULL);
        """
        query_args = [tuple(product_ids_to_ignore), other_period_start]

        self.env.cr.execute(query, tuple(query_args))
        result = self.env.cr.fetchall()

        other_product_ids = [x[0] for x in result]

        if other_period_end == fields.Date.to_string(date_today):
            qty_to_check = len(other_product_ids)
        else:
            qty_to_check = int(len(other_product_ids) /
                               (days / other_period_nbr_year))

        if qty_to_check >= other_product_ids:
            product_ids.update(other_product_ids)
        else:
            product_sample_ids = random.sample(other_product_ids, qty_to_check)
            product_ids.update(product_sample_ids)

        return self.browse(product_ids)
