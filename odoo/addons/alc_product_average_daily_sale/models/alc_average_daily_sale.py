# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import api, fields, models

import odoo.addons.decimal_precision as dp


class AlcAverageDailySale(models.Model):

    _name = "alc.average.daily.sale"
    _auto = False

    product_id = fields.Many2one("product.product", "Product", required=True)
    average_qty_by_sale = fields.Float(help="Average Daily Sales Qty", required=True)
    average_daily_sales_count = fields.Integer(
        help="Avarage Daily Sales Count", required=True
    )
    std_dev = fields.Float("Qty Standard Deviation", required=True)
    nbr_sales = fields.Integer(required=True)
    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", required=True)
    date_from = fields.Date("From", required=True)
    date_to = fields.Date("To", required=True)
    config_id = fields.Many2one(
        string="computation parameters",
        comodel_name="alc.product.average.daily.sale.config",
        required=True,
    )
    safety_bin_min_qty = fields.Float(
        digits=dp.get_precision("Product Unit of Measure"),
        help="Minimal safety qty into a bin location",
    )

    @api.model
    def get_refresh_date(self):
        return self.env["ir.config_parameter"].get_param(
            "alc_average_daily_sale_refresh_date"
        )

    @api.model
    def set_refresh_date(self, date=None):
        if date is None:
            date = fields.Datetime.now()
        self.env["ir.config_parameter"].set_param(
            "alc_average_daily_sale_refresh_date", date
        )

    @api.model
    def refresh_view(self):
        self.env.cr.execute("refresh materialized view %s", (AsIs(self._table),))
        self.set_refresh_date()

    def init(self):
        self.env.cr.execute(
            "DROP MATERIALIZED VIEW IF EXISTS %s CASCADE", (AsIs(self._table),)
        )
        self.env.cr.execute(
            """
            CREATE MATERIALIZED VIEW %s AS (
-- Create a consolidated definition of parameters used into the average daily
-- sales computation. Parameters are specified by product ABC class
WITH cfg AS (
    SELECT
        *,
        -- end of the analyzed period
        NOW()::date as date_to,
        -- start of the analyzed perciod computed from the original cfg
        (NOW() - (period_value::TEXT || ' ' || period_name::TEXT)::INTERVAL):: date as date_from,
        -- the number of business days between start and end computed by
        -- removing saturday and sunday
        (SELECT count(1) from (select EXTRACT(DOW FROM s.d::date) as dd
            FROM generate_series(
            (NOW() - (period_value::TEXT || ' ' || period_name::TEXT)::INTERVAL):: date ,
             NOW()::date,
             '1 day') AS s(d)) t
            WHERE dd not in(0,6)) AS nrb_days_without_sat_sun
    FROM
        alc_product_average_daily_sale_config
),
-- Create a consolidated view of all the stock moves from internal locations
-- to customer location. The consolidation is done by including all the moves
-- with a date done into the period provided by the configuration for each
-- product according to its abc classification.
-- The consolidated view also include the standard deviation of the product qty
-- sold at once, and the lower and upper bounds to use to exclude qties
-- that diverge too much from the average qty by product. The factor applied
-- to the standard deviation to compute the lower and upper bounds is also
-- provided by the configuration according the product's abc classification
-- All the products without abc classification are linked to the 'C' class
deliveries_last AS (
    SELECT
        sm.product_id,
        sm.product_uom_qty,
        sm.warehouse_id,
        (avg(product_uom_qty) OVER pid
            - (stddev_samp(product_uom_qty) OVER pid * cfg.stddev_exclude_factor)
        )  as lower_bound,
        (avg(product_uom_qty) OVER pid
            + ( stddev_samp(product_uom_qty) OVER pid * cfg.stddev_exclude_factor)
        ) as upper_bound,
        coalesce ((stddev_samp(product_uom_qty) OVER pid), 0) as std_dev,
        cfg.nrb_days_without_sat_sun,
        cfg.date_from,
        cfg.date_to,
        cfg.id as config_id
    FROM stock_move sm
        JOIN stock_location sl_src ON sm.location_id = sl_src.id
        JOIN stock_location sl_dest ON sm.location_dest_id = sl_dest.id
        JOIN product_product pp on pp.id = sm.product_id
        JOIN cfg on cfg.abc_classification_level = coalesce(pp.abc_storage, 'c')
    WHERE
      sl_src.usage in ('view', 'internal')
      AND sl_dest.usage = 'customer'
      AND sm.priority > '0'
      AND sm.date BETWEEN cfg.date_from AND cfg.date_to
      AND sm.state = 'done'
      AND sm.warehouse_id is not null
    WINDOW pid AS (PARTITION BY sm.product_id, sm.warehouse_id)
),

averages AS(
   SELECT
        concat(warehouse_id, product_id)::integer as id,
        product_id,
        warehouse_id,
        (avg(product_uom_qty) FILTER
            (WHERE product_uom_qty BETWEEN lower_bound AND upper_bound OR std_dev = 0)
            )::numeric AS average_qty_by_sale,
        (count(product_uom_qty) FILTER
            (WHERE product_uom_qty BETWEEN lower_bound AND upper_bound OR std_dev = 0)
            / nrb_days_without_sat_sun)::numeric AS average_daily_sales_count,
        count(product_uom_qty) FILTER
            (WHERE product_uom_qty BETWEEN lower_bound AND upper_bound OR std_dev = 0)::double precision as nbr_sales,
        std_dev::numeric ,
        date_from,
        date_to,
        config_id
    FROM deliveries_last
    GROUP BY product_id, warehouse_id, std_dev, nrb_days_without_sat_sun, date_from, date_to, config_id
)
-- Collect the data for the materialized view
    SELECT
        t.id,
        product_id,
        t.warehouse_id,
        average_qty_by_sale,
        average_daily_sales_count,
        nbr_sales,
        std_dev,
        date_from,
        date_to,
        config_id,
        cfg.number_days_qty_in_stock * GREATEST(average_daily_sales_count, 1)  * (average_qty_by_sale + (std_dev * cfg.stddev_include_factor)) as safety_bin_min_qty
    FROM averages t
    JOIN alc_product_average_daily_sale_config cfg on cfg.id = t.config_id
) WITH NO DATA;""",
            (AsIs(self._table),),
        )
        self.env.cr.execute(
            "CREATE UNIQUE INDEX pk_%s ON %s (id)",
            (AsIs(self._table), AsIs(self._table)),
        )
        self.env.cr.execute(
            "CREATE INDEX %s_product_id_idx ON %s (product_id)",
            (AsIs(self._table), AsIs(self._table)),
        )
        self.env.cr.execute(
            "CREATE INDEX %s_warehouse_id_idx ON %s (warehouse_id)",
            (AsIs(self._table), AsIs(self._table)),
        )
        self.set_refresh_date(date=False)
        cron = self.env.ref(
            "alc_product_average_daily_sale.refresh_materialized_view",
            # at install, won't exist yet
            raise_if_not_found=False,
        )
        # refresh data asap, but not during the upgrade
        if cron:
            cron.nextcall = fields.Datetime.now()
