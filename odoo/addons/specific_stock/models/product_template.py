# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    life_time = fields.Integer(related="categ_id.life_time")

    use_time = fields.Integer(related="categ_id.use_time")

    removal_time = fields.Integer(related="categ_id.removal_time")

    alert_time = fields.Integer(related="categ_id.alert_time")

    picking_zone_id = fields.Many2one(
        "picking.zone",
        string="Picking zone",
        compute="_compute_picking_zone_id",
        readonly=True,
        store=True,
    )
    is_mto_product = fields.Boolean(
        "On Order", readonly=True, compute="_compute_picking_zone_id", store=True
    )

    @api.depends("route_ids", "route_from_categ_ids")
    def _compute_picking_zone_id(self):
        Rule = self.env["procurement.rule"]
        stock_location = self.env.ref("stock.stock_location_stock")
        picking_types = self.env["stock.picking.type"].search(
            [("default_location_src_id", "child_of", stock_location.id)]
        )
        route_mto = self.env.ref("stock.route_warehouse0_mto")

        for product in self:
            product_routes = product.route_ids | product.categ_id.total_route_ids

            product.is_mto_product = route_mto in product_routes
            # We need to remove the MTO route because this route has a higher
            # priority but we want to compute the picking zone only on
            # "standard" route
            product_routes -= route_mto

            res = Rule.search(
                [
                    ("route_id", "in", product_routes.ids),
                    ("picking_type_id", "in", picking_types.ids),
                ],
                order="route_sequence, sequence",
                limit=1,
            )
            if res:
                product.picking_zone_id = res.picking_type_id.picking_zone_id.id


# Due to a bug in odoo 10 we need to redefine the fields
class ProductProduct(models.Model):
    _inherit = "product.product"

    life_time = fields.Integer(related="categ_id.life_time")

    use_time = fields.Integer(related="categ_id.use_time")

    removal_time = fields.Integer(related="categ_id.removal_time")

    alert_time = fields.Integer(related="categ_id.alert_time")

    date_last_inventory = fields.Datetime("Last inventory", readonly=True)

    @api.model
    def get_number_of_products_by_category(self):
        """
        Return the number of products by categories
        :return:
        """
        config_param = self.env["ir.config_parameter"]
        best_sellers_percent = int(
            config_param.get_param("stock.best_sellers_percent", 0)
        )

        all_products_query = """
        SELECT count(*)
        FROM product_product AS product
          INNER JOIN product_template AS product_tmpl
            ON product.product_tmpl_id = product_tmpl.id
        WHERE product.active = TRUE
        AND product_tmpl.type = 'product';
        """
        self.env.cr.execute(all_products_query)
        nbr_products = self.env.cr.fetchone()[0]

        price = float(
            self.env["ir.config_parameter"].get_param(
                "stock.price_limit_for_inventory", 0
            )
        )
        expensive_products_query = """
        SELECT count(*)
        FROM product_product AS product
          INNER JOIN product_template AS product_tmpl
            ON product.product_tmpl_id = product_tmpl.id
        WHERE product_tmpl.list_price >= %s
        AND product.active = TRUE
        AND product_tmpl.type = 'product';
        """
        self.env.cr.execute(expensive_products_query, (price,))
        nbr_expensive_products = self.env.cr.fetchone()[0]

        # Take a percent of the number of products
        # to compute the number of best sellers to take.
        # To modify the percent of best sellers change the config
        # "Quantity to take for best sellers (in percent)" in sock settings
        nbr_best_sellers = int(nbr_products * (best_sellers_percent / 100.0))
        nbr_other_products = nbr_products - nbr_expensive_products - nbr_best_sellers

        return nbr_expensive_products, nbr_best_sellers, nbr_other_products

    @api.model
    def get_products_daily_inventory(
        self, inventory_periods, date_today_overwrite=None
    ):
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
        config_param = self.env["ir.config_parameter"]
        price = float(config_param.get_param("stock.price_limit_for_inventory", 0))
        days = int(config_param.get_param("stock.nbr_open_days", 0))
        interval_between_inventory = int(
            config_param.get_param("stock.months_between_inventory", 0)
        )
        best_sellers_duration = int(
            config_param.get_param("stock.best_sellers_duration", 0)
        )
        date_today = date_today_overwrite or date.today()
        maximum_last_inventory_date = date_today - relativedelta(
            months=interval_between_inventory
        )
        maximum_last_inventory_date_str = fields.Date.to_string(
            maximum_last_inventory_date
        )

        if not price or not days:
            raise UserError(
                _(
                    "Please set the Price limit for inventory "
                    "or/and the Number of open days "
                    "in the stock configuration"
                )
            )

        product_ids = set()

        product_ids_in_open_inventory_query = """
        SELECT DISTINCT sil.product_id
        FROM stock_inventory_line AS sil
            INNER JOIN stock_inventory AS si
                ON sil.inventory_id = si.id
        WHERE si.state = 'confirm';
        """
        self.env.cr.execute(product_ids_in_open_inventory_query)
        product_ids_in_open_inventory = {x[0] for x in self.env.cr.fetchall()}
        # Psycopg2 doesn't allow to create a request with an empty list.
        # To avoid to overcomplicate the code, I prefer to add a fake ID
        # in the list.
        product_ids_in_open_inventory.add(0)

        (
            nbr_expensive_products,
            nbr_best_sellers,
            nbr_other,
        ) = self.get_number_of_products_by_category()

        # Expensive products
        # ------------------
        # An expensive product is a product where the price is greater or
        # equal to the "limit" price defined in the stock configuration.
        expensive_period = inventory_periods.get("expensive")
        if not expensive_period:
            raise UserError(_("There is no period for expensive products"))
        expensive_period_start = expensive_period["date_start"]
        expensive_period_nbr_year = expensive_period["nbr_inventory_per_year"]

        if maximum_last_inventory_date_str < expensive_period_start:
            expensive_period_start = maximum_last_inventory_date_str

        qty_to_check = int(nbr_expensive_products / (days / expensive_period_nbr_year))

        query = """
        SELECT product.id
        FROM product_product AS product
          INNER JOIN product_template AS product_tmpl
            ON product.product_tmpl_id = product_tmpl.id
        WHERE product_tmpl.list_price >= %s
        AND (product.date_last_inventory < %s
             OR product.date_last_inventory IS NULL)
        AND product_tmpl.is_mto_product = FALSE
        AND product.active = TRUE
        AND product_tmpl.type = 'product'
        AND product.id NOT IN %s
        ORDER BY random()
        LIMIT %s;
        """
        query_args = [
            price,
            expensive_period_start,
            tuple(product_ids_in_open_inventory),
            qty_to_check,
        ]

        self.env.cr.execute(query, tuple(query_args))
        result = self.env.cr.fetchall()
        expensive_products_ids = [x[0] for x in result]

        product_ids.update(expensive_products_ids)

        # Best sellers
        # ------------------
        # Take twenty percent of best sales
        best_sellers_period = inventory_periods.get("best_sellers")
        if not best_sellers_period:
            raise UserError(_("There is no period for best sellers products"))
        best_sellers_period_start = best_sellers_period["date_start"]
        best_sellers_period_nbr_year = best_sellers_period["nbr_inventory_per_year"]

        if maximum_last_inventory_date_str < best_sellers_period_start:
            best_sellers_period_start = maximum_last_inventory_date_str

        qty_to_check = int(nbr_best_sellers / (days / best_sellers_period_nbr_year))

        query = """
        SELECT product_id
        FROM (
            SELECT line.product_id, count(*) AS cnt
            FROM sale_order_line AS line
              INNER JOIN product_product AS product
                ON line.product_id = product.id
              INNER JOIN product_template AS product_tmpl
                ON product.product_tmpl_id = product_tmpl.id
            WHERE line.create_date > (NOW() - INTERVAL '%s MONTHS')
             AND (product.date_last_inventory < %s
                  OR product.date_last_inventory IS NULL)
             AND product.active = TRUE
             AND product_tmpl.type = 'product'
             AND product.id NOT IN %s
             AND product_tmpl.is_mto_product = FALSE
            GROUP BY line.product_id
            ORDER BY cnt DESC
            LIMIT %s
          ) AS result
        ORDER BY random()
        LIMIT %s;
        """
        query_args = [
            best_sellers_duration,
            best_sellers_period_start,
            tuple(product_ids | product_ids_in_open_inventory),
            nbr_best_sellers,
            qty_to_check,
        ]
        self.env.cr.execute(query, tuple(query_args))
        best_sellers_ids = [x[0] for x in self.env.cr.fetchall()]

        product_ids.update(best_sellers_ids)

        # Others
        # ------
        # Take all others products
        other_period = inventory_periods.get("other")
        if not other_period:
            raise UserError(_("There is no period for other products"))
        other_period_start = other_period["date_start"]
        other_period_nbr_year = other_period["nbr_inventory_per_year"]

        if maximum_last_inventory_date_str < other_period_start:
            other_period_start = maximum_last_inventory_date_str

        qty_to_check = int(nbr_other / (days / other_period_nbr_year))

        query = """
        SELECT product.id
        FROM product_product AS product
          INNER JOIN product_template AS product_tmpl
            ON product.product_tmpl_id = product_tmpl.id
        WHERE (product.date_last_inventory < %s
          OR product.date_last_inventory IS NULL)
        AND product.active = TRUE
        AND product_tmpl.type = 'product'
        AND product.id NOT IN %s
        AND product_tmpl.is_mto_product = FALSE
        ORDER BY random()
        LIMIT %s;
        """
        self.env.cr.execute(
            query,
            (
                other_period_start,
                tuple(product_ids | product_ids_in_open_inventory),
                qty_to_check,
            ),
        )
        result = self.env.cr.fetchall()

        other_product_ids = [x[0] for x in result]

        product_ids.update(other_product_ids)

        return self.browse(product_ids)
