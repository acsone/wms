# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.alc_materialized_view_mixin.models import materialized_view_mixin
from odoo.addons.base.models.res_partner import Partner
from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.product.models.product_template import ProductTemplate


class AlcEshopProductOrderedQty(materialized_view_mixin.MaterializedViewMixin):
    _name = "alc.eshop.product.ordered.qty"
    _description = "Product Ordered Qty"
    _auto = False
    _abstract = False

    ordered_count = fields.Integer(readonly=True)
    partner_id = fields.Many2one[Partner](readonly=True)
    product_id = fields.Many2one[ProductProduct](readonly=True)
    product_tmpl_id = fields.Many2one[ProductTemplate](readonly=True)
    is_food = fields.Boolean(readonly=True)
    is_meds = fields.Boolean(readonly=True)
    is_equipment = fields.Boolean(readonly=True)
    in_supplier_promotion = fields.Boolean(readonly=True)
    date_last_ordered = fields.Date(readonly=True)

    @api.model
    def get_init_query(self):
        return """
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
            AND date_start <= CURRENT_DATE AND date_end >= CURRENT_DATE
            AND (COALESCE(discount_sale, 0) > 0   or  COALESCE(ratio_main_product, 0) > 0)
        ) AS in_supplier_promotion,
    MAX(date_order) AS date_last_ordered
FROM
    sale_order_line sol
    JOIN sale_order so ON so.id =  sol.order_Id
    JOIN product_product pp ON sol.product_id = pp.id
    JOIN product_template pt ON pp.product_tmpl_id = pt.id
where
    so.sale_channel_id IN %(channels)s
    AND so.state in ('done', 'sale')
    AND (pt.is_food OR pt.is_meds OR pt.is_equipment)
    AND date_order >= DATE_TRUNC('month', NOW() - INTERVAL '1 year')

GROUP BY so.partner_id, sol.product_id, pp.product_tmpl_id, pt.is_food, pt.is_equipment, pt.is_meds
HAVING SUM(product_uom_qty - COALESCE(product_qty_canceled, 0) ) > 0
ORDER BY partner_id, SUM(product_uom_qty - COALESCE(product_qty_canceled, 0) ) DESC

);

CREATE UNIQUE INDEX pk_%(table)s ON %(table)s (id);

CREATE INDEX idx_%(table)s_partner_id_index ON %(table)s (partner_id);
"""

    @api.model
    def get_init_query_args(self):
        args = super().get_init_query_args()
        channels = tuple(self.env["sale.channel"]._get_internal_ids())
        args["channels"] = channels
        return args
