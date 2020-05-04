# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from psycopg2.extensions import AsIs

from odoo import api, models, tools


class AccountInvoiceLineMarginReport(models.AbstractModel):
    """This SQL view is used by QlickView."""

    _name = "account.invoice.line.margin"

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        sql_view_query = """
            CREATE OR REPLACE VIEW account_invoice_line_margin AS (
                SELECT
                    ai.date,
                    ail.*,
                    pph.cost AS unit_cost,
                    unit_net_price,
                    (unit_net_price - pph.cost) AS unit_margin
                FROM account_invoice_line ail
                LEFT JOIN account_invoice ai
                    ON ail.invoice_id = ai.id
                LEFT JOIN LATERAL (
                    SELECT
                        pph.cost
                    FROM product_price_history pph
                    WHERE
                        ail.product_id = pph.product_id AND
                        ai.date >= pph.datetime::date
                    ORDER BY pph.datetime DESC
                    LIMIT 1
                ) pph ON TRUE,
                LATERAL(
                    SELECT ROUND(
                        price_unit
                        * (1 - discount2 / 100)
                        * (1 - discount3 / 100), 2))
                    AS al(unit_net_price)
            )
        """
        args = (AsIs(self._table),)
        self.env.cr.execute(sql_view_query, args)
