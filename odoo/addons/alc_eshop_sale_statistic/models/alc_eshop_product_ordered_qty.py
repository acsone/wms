# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import api, fields, models


class AlcEshopProductOrderedQty(models.Model):

    _name = "alc.eshop.product.ordered.qty"
    _description = "Product Ordered Qty"
    _auto = False

    ordered_count = fields.Integer(readonly=True)
    partner_id = fields.Many2one(comodel_name="res.partner", readonly=True)
    product_id = fields.Many2one(comodel_name="product.product", readonly=True)
    product_tmpl_id = fields.Many2one(comodel_name="product.template", readonly=True)
    is_food = fields.Boolean(readonly=True)
    is_meds = fields.Boolean(readonly=True)
    is_equipment = fields.Boolean(readonly=True)
    in_supplier_promotion = fields.Boolean(readonly=True)
    date_last_ordered = fields.Date(readonly=True)

    @api.model
    def get_refresh_date(self):
        return self.env["ir.config_parameter"].get_param(
            "alc_eshop_product_ordered_qty_refresh_date"
        )

    @api.model
    def set_refresh_date(self, date=None):
        if date is None:
            date = fields.Datetime.now()
        self.env["ir.config_parameter"].set_param(
            "alc_eshop_product_ordered_qty_refresh_date", date
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
            CREATE MATERIALIZED VIEW %(table)s AS (

SELECT
    ROW_NUMBER() OVER (ORDER BY  partner_id, SUM(product_uom_qty - COALESCE(product_qty_canceled, 0) ) DESC) AS id,
    SUM(product_uom_qty - COALESCE(product_qty_canceled, 0) ) AS ordered_count,
    so.partner_id,
    sol.product_id,
    pp.product_tmpl_id,
    pt.is_food,
    pt.is_meds,
    pt.is_equipment,
    EXISTS (
        SELECT
            1
        FROM
            product_supplierinfo ps
        WHERE
            ps.product_tmpl_id=pp.product_tmpl_id
            AND date_start <= NOW() AND date_end >= NOW()
            AND (discount_sale IS NOT NULL or ratio_main_product IS NOT NULL)
        ) AS in_supplier_promotion,
    MAX(date_order) AS date_last_ordered
FROM
    sale_order_line sol
    JOIN sale_order so ON so.id =  sol.order_Id
    JOIN product_product pp ON sol.product_id = pp.id
    JOIN product_template pt ON pp.product_tmpl_id = pt.id
where
    so.sale_channel IN ('web', 'mail', 'phone', 'fax')
    AND so.state in ('done', 'sale')
    AND date_order >= DATE_TRUNC('month', NOW() - INTERVAL '1 year')

GROUP BY so.partner_id, sol.product_id, pp.product_tmpl_id, pt.is_food, pt.is_equipment, pt.is_meds
ORDER BY partner_id, SUM(product_uom_qty - COALESCE(product_qty_canceled, 0) ) DESC

);

CREATE UNIQUE INDEX pk_%(table)s ON %(table)s (id);

CREATE INDEX idx_%(table)s_partner_id_index ON %(table)s (partner_id);
""",
            {"table": AsIs(self._table)},
        )
        self.set_refresh_date(date=False)
        cron = self.env.ref(
            "alc_eshop_sale_statistic.refresh_materialized_view",
            # at install, won't exist yet
            raise_if_not_found=False,
        )
        # refresh data asap, but not during the upgrade
        if cron:
            cron.nextcall = fields.Datetime.now()
