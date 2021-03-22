# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import api, fields, models

import odoo.addons.decimal_precision as dp
from odoo.addons.stock_storage_type_putaway_abc.models.stock_location import (
    ABC_SELECTION,
)


class AlcAverageDailySale(models.Model):

    _name = "alc.average.daily.sale"
    _auto = False
    _order = "abc_classification_level ASC, product_id ASC"

    abc_classification_level = fields.Selection(
        selection=ABC_SELECTION, required=True, read_only=True, index=True
    )
    average_daily_sales_count = fields.Float(
        help="Avarage Daily Sales Count", required=True
    )
    average_qty_by_sale = fields.Float(help="Average Daily Sales Qty", required=True)
    average_daily_qty = fields.Float(help="The average daily qty sold", required=True)
    config_id = fields.Many2one(
        string="computation parameters",
        comodel_name="alc.product.average.daily.sale.config",
        required=True,
    )
    date_from = fields.Date("From", required=True)
    date_to = fields.Date("To", required=True)
    is_mto_product = fields.Boolean(
        string="On Order", readonly=True, store=True, index=True,
    )
    nbr_sales = fields.Integer(required=True)
    picking_zone_id = fields.Many2one(
        string="Picking zone", comodel_name="picking.zone", readonly=True, index=True,
    )
    product_id = fields.Many2one(
        "product.product", "Product", required=True, index=True
    )
    safety = fields.Float(
        required=True,
        help="daily stddev * safety factor * sqrt(nbr days into period "
        "without sat and sun",
    )
    safety_bin_min_qty = fields.Float(
        requied=True,
        digits=dp.get_precision("Product Unit of Measure"),
        help="Minimal safety qty into a bin location computed as: "
        "average daily qty * number days in stock * safety",
    )
    safety_bin_min_qty_old = fields.Float(
        requied=True,
        digits=dp.get_precision("Product Unit of Measure"),
        help="Minimal value for the safety qty. Computed as: "
        "number days in stock * GREATEST(average daily sales count, 1) * "
        "(average qty by sale + (stddev * safety factor))",
    )
    sale_ok = fields.Boolean(
        string="Can be Sold",
        readonly=True,
        index=True,
        help="Specify if the product can be selected in a sales order line.",
    )
    stddev = fields.Float("Qty Standard Deviation", required=True)
    stddev_daily = fields.Float("Daily Qty Standard Deviation", required=True)
    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", required=True)

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
        NOW()::date - '1 day'::interval as date_to,
        -- start of the analyzed perciod computed from the original cfg
        (NOW() - (period_value::TEXT || ' ' || period_name::TEXT)::INTERVAL):: date as date_from,
        -- the number of business days between start and end computed by
        -- removing saturday and sunday
        (SELECT count(1) from (select EXTRACT(DOW FROM s.d::date) as dd
            FROM generate_series(
            (NOW() - (period_value::TEXT || ' ' || period_name::TEXT)::INTERVAL):: date ,
             (NOW()- '1 day'::interval)::date,
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
        coalesce ((stddev_samp(product_uom_qty) OVER pid), 0) as stddev,
        cfg.nrb_days_without_sat_sun,
        cfg.date_from,
        cfg.date_to,
        cfg.id as config_id,
        sm.date
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
            (WHERE product_uom_qty BETWEEN lower_bound AND upper_bound OR stddev = 0)
            )::numeric AS average_qty_by_sale,
        (count(product_uom_qty) FILTER
            (WHERE product_uom_qty BETWEEN lower_bound AND upper_bound OR stddev = 0)
            / nrb_days_without_sat_sun::numeric) AS average_daily_sales_count,
        count(product_uom_qty) FILTER
            (WHERE product_uom_qty BETWEEN lower_bound AND upper_bound OR stddev = 0)::double precision as nbr_sales,
        stddev::numeric ,
        date_from,
        date_to,
        config_id,
        nrb_days_without_sat_sun
    FROM deliveries_last
    GROUP BY product_id, warehouse_id, stddev, nrb_days_without_sat_sun, date_from, date_to, config_id
),

-- Compute the standard deviation of the average daily sales count
-- excluding saturday and sunday
daily_stddev AS(
    SELECT
        id,
        product_id,
        warehouse_id,
        stddev_samp(daily_sales) as stddev_daily
        from (
            SELECT
                to_char(date_trunc('day', date), 'YYYY-MM-DD'),
                concat(warehouse_id, product_id)::integer as id,
                product_id,
                warehouse_id,
                (count(product_uom_qty) FILTER
                    (WHERE product_uom_qty BETWEEN lower_bound AND upper_bound OR stddev = 0)
                ) as daily_sales
            FROM deliveries_last
            WHERE EXTRACT(DOW FROM date) <> '0' AND EXTRACT(DOW FROM date) <> '6'
            GROUP BY product_id, warehouse_id, 1
        ) as averages_daily group by id, product_id, warehouse_id

)

-- Collect the data for the materialized view
    SELECT
        t.id,
        t.product_id,
        t.warehouse_id,
        average_qty_by_sale,
        average_daily_sales_count,
        average_qty_by_sale * average_daily_sales_count as average_daily_qty,
        nbr_sales,
        stddev,
        date_from,
        date_to,
        config_id,
        abc_classification_level,
        picking_zone_id,
        sale_ok,
        is_mto_product,
        ds.stddev_daily,
        ds.stddev_daily * cfg.safety_factor * sqrt(nrb_days_without_sat_sun) as  safety,
        (cfg.number_days_qty_in_stock * average_qty_by_sale * average_daily_sales_count) + (ds.stddev_daily * cfg.safety_factor * sqrt(nrb_days_without_sat_sun)) as safety_bin_min_qty_new,
        cfg.number_days_qty_in_stock * GREATEST(average_daily_sales_count, 1)  * (average_qty_by_sale + (stddev * cfg.safety_factor)) as safety_bin_min_qty_old,
        GREATEST(
            (cfg.number_days_qty_in_stock * average_qty_by_sale * average_daily_sales_count) + (ds.stddev_daily * cfg.safety_factor * sqrt(nrb_days_without_sat_sun)),
            (cfg.number_days_qty_in_stock *  average_qty_by_sale)
        ) as safety_bin_min_qty
    FROM averages t
    JOIN daily_stddev ds on ds.id= t.id
    JOIN alc_product_average_daily_sale_config cfg on cfg.id = t.config_id
    JOIN product_product pp on pp.id = t.product_id
    JOIN product_template pt on pt.id = pp.product_tmpl_id
    ORDER BY product_id
) WITH NO DATA;""",
            (AsIs(self._table),),
        )
        self.env.cr.execute(
            "CREATE UNIQUE INDEX pk_%s ON %s (id)",
            (AsIs(self._table), AsIs(self._table)),
        )
        for name, field in self._fields.iteritems():
            if not field.index:
                continue
            self.env.cr.execute(
                "CREATE INDEX %s_%s_idx ON %s (%s)",
                (AsIs(self._table), AsIs(name), AsIs(self._table), AsIs(name)),
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
