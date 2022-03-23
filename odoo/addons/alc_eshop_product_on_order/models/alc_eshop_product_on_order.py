# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import api, fields, models
from odoo.tools.sql import drop_view_if_exists

from ..exceptions import NoBackOrderError


class AlcEshopProductOnOrder(models.Model):

    _name = "alc.eshop.product.on.order"
    _description = "Alc Eshop Product On Order"
    _auto = False

    product_id = fields.Many2one(comodel_name="product.product", readonly=True)
    order_id = fields.Many2one(comodel_name="sale.order", readonly=True)
    order_line_id = fields.Many2one(comodel_name="sale.order.line", readonly=True)
    partner_id = fields.Many2one(comodel_name="res.partner", readonly=True)
    description = fields.Char(readonly=True)
    order_ref = fields.Char(readonly=True)
    customer_ref = fields.Char(readonly=True)
    qty_ordered = fields.Float(readonly=True)
    qty_to_deliver = fields.Float(readonly=True)
    qty_unavailable = fields.Float(readonly=True, help="unavailable at SO confirmation")
    qty_backorder = fields.Float(
        readonly=True, help="only for product not available at SO confirmation"
    )
    is_mto = fields.Boolean(readonly=True)
    is_meds = fields.Boolean(readonly=True)
    is_equipment = fields.Boolean(readonly=True)
    is_food = fields.Boolean(readonly=True)

    @api.model_cr
    def init(self):
        self._create_index()
        self._create_view()

    @api.model_cr
    def _create_index(self):
        # create index required by the view
        index_name = "idx_%s_index" % self._table
        self.env.cr.execute(
            "SELECT indexname FROM pg_indexes WHERE indexname = %s", (index_name,),
        )
        if not self.env.cr.fetchone():
            self.env.cr.execute(
                """
        CREATE INDEX %(index_name)s
        ON %(table)s (order_partner_id)
        WHERE
            product_qty_remains_to_deliver > 0
            AND product_type in ('consu', 'product')
            AND is_consignment = false
            AND state not in ('draft', 'cancel')
                """,
                dict(
                    index_name=AsIs(index_name),
                    table=AsIs(self.env["sale.order.line"]._table),
                ),
            )

    @api.model_cr
    def _create_view(self):
        # create the view
        drop_view_if_exists(self._cr, self._table)
        query = """
            CREATE OR REPLACE VIEW %(table)s AS (
SELECT
    sol.id,
    so.id as order_id,
    sol.id as order_line_id,
    sol.product_id,
    sol.name as description,
    so.name as order_ref,
    so.date_order as order_date,
    so.client_order_ref as customer_ref,
    sol.product_uom_qty as qty_ordered,
    sol.product_qty_remains_to_deliver as qty_to_deliver,
    sol.product_qty_unavailable as qty_unavailable,
    sol.order_partner_id as partner_id,
    CASE
        WHEN
            sol.product_qty_unavailable <> 0
            AND sol.qty_delivered = 0
            AND sol.product_qty_canceled = 0
        THEN sol.product_qty_unavailable
        WHEN
            sol.product_qty_unavailable <> 0
            AND (sol.qty_delivered <> 0 OR sol.product_qty_canceled <> 0)
        THEN sol.product_qty_remains_to_deliver
        ELSE 0
    END as qty_backorder,
    pt.is_mto_product as is_mto,
    pt.is_meds,
    pt.is_equipment,
    pt.is_food
FROM
    sale_order_line sol
    JOIN sale_order so on so.id = sol.order_id
    JOIN product_product pp on pp.id = sol.product_id
    JOIN product_template pt on pt.id = pp.product_tmpl_id
WHERE
    sol.product_qty_remains_to_deliver > 0
    AND sol.product_type in ('consu', 'product')
    AND sol.is_consignment = False
    AND sol.state not in ('draft', 'cancel')
    AND so.sale_channel IN %(channels)s
            )
                """
        channels = tuple(self.env["sale.order"]._get_sale_channels_internal())
        self._cr.execute(query, dict(table=AsIs(self._table), channels=channels))

    def request_backorder_cancellation(self, quantity):
        for record in self:
            if not record.qty_unavailable:
                raise NoBackOrderError(record.product_id.name, record.order_ref)
        template = self.env.ref(
            "alc_eshop_product_on_order.sale_order_request_backorder_cancellation"
        )
        for record in self:
            template.with_context(
                product=record.product_id, quanity=quantity
            ).send_mail(record.order_id.id)
