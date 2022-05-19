# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AlcEshopProductOrderedYearly(models.Model):

    _name = "alc.eshop.product.ordered.yearly"
    _inherit = "materialized.view.mixin"
    _description = "Yearly Ordered Product"
    _auto = False

    total = fields.Float(readonly=True)
    order_year = fields.Integer(readonly=True)
    partner_id = fields.Many2one(comodel_name="res.partner", readonly=True)
    product_id = fields.Many2one(comodel_name="product.product", readonly=True)
    product_tmpl_id = fields.Many2one(comodel_name="product.template", readonly=True)
    is_food = fields.Boolean(readonly=True)
    is_meds = fields.Boolean(readonly=True)
    is_equipment = fields.Boolean(readonly=True)

    @api.model
    def get_init_query(self):
        return """CREATE MATERIALIZED VIEW %(table)s AS (
SELECT
    ROW_NUMBER() OVER (ORDER BY partner_id) AS id,
    so.partner_id,
    SUM(qty_to_invoice * price_reduce_taxexcl) AS total,
    extract(year from so.date_order)::INTEGER AS order_year,
    pt.is_food,
    pt.is_meds,
    pt.is_equipment
FROM
    sale_order_line sol
    JOIN sale_order so ON so.id =  sol.order_Id
    JOIN product_product pp ON sol.product_id = pp.id
    JOIN product_template pt ON pp.product_tmpl_id = pt.id
where
    so.sale_channel IN %(channels)s
    AND so.state in ('done', 'sale')
    AND date_order > DATE_TRUNC('year', NOW() - INTERVAL '5 year')
    GROUP BY so.partner_id, order_year, pt.is_food, pt.is_equipment, pt.is_meds
ORDER BY partner_id
);

CREATE UNIQUE INDEX pk_%(table)s ON %(table)s (id);

CREATE INDEX idx_%(table)s_partner_id_index ON %(table)s (partner_id);
"""

    @api.model
    def get_init_query_args(self):
        args = super(AlcEshopProductOrderedYearly, self).get_init_query_args()
        channels = tuple(self.env["sale.order"]._get_sale_channels_internal())
        args["channels"] = channels
        return args
