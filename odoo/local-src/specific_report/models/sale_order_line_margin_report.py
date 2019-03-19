# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from psycopg2.extensions import AsIs

from odoo import api, models, tools


class SaleOrderLineMarginReport(models.AbstractModel):
    """This SQL view is used by QlickView."""

    _name = 'sale.order.line.margin'

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        sql_view_query = """
            CREATE OR REPLACE VIEW sale_order_line_margin AS (
                SELECT DISTINCT ON (sol.id, pph.product_id)
                    so.date_order,
                    sol.*,
                    pph.cost AS unit_cost,
                    unit_net_price,
                    (unit_net_price - pph.cost) AS unit_margin
                FROM sale_order_line sol
                LEFT JOIN sale_order so
                    ON sol.order_id = so.id
                LEFT JOIN product_price_history pph
                    ON sol.product_id = pph.product_id
                        AND so.date_order::date >= pph.datetime::date,
                LATERAL(
                    SELECT ROUND(
                        price_unit
                        * (1 - discount2 / 100)
                        * (1 - discount3 / 100), 2))
                    AS sl(unit_net_price)
                ORDER BY sol.id, pph.product_id, pph.datetime DESC
            )
        """
        args = (AsIs(self._table),)
        self.env.cr.execute(sql_view_query, args)
