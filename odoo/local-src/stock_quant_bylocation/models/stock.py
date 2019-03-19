# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2016 BCIM sprl, Camptocamp
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models
from odoo.tools.sql import drop_view_if_exists


class ReportStockQuantBylocation(models.Model):
    _name = 'report.stock.quant.bylocation'
    _auto = False

    def _prepare_init(self):
        return {
            "select": """
                    min(quant.id) AS id
                , quant.product_id AS product_id
                , quant.location_id AS location_id
                , sum(quant.qty) AS qty
                , quant.owner_id AS owner_id
                , quant.company_id AS company_id
                , quant.reservation_id AS reservation_id
                """,
            "join": "",
            "where": "",
            "groupby": "quant.product_id, quant.location_id, quant.owner_id, "
            "quant.company_id, quant.reservation_id",
            "orderby": "",
        }

    def init(self):
        drop_view_if_exists(self.env.cr, self._table)
        params = self._prepare_init()
        query = """
        SELECT %(select)s
        FROM stock_quant quant
        LEFT join product_product product ON quant.product_id=product.id
        %(join)s
        WHERE qty >= 0
        %(where)s
        GROUP BY %(groupby)s
        """
        if params.get('orderby'):
            query += "ORDER BY %(orderby)s"
        self.env.cr.execute(
            "CREATE OR REPLACE VIEW "
            + self._table
            + " AS ("
            + query % params
            + ")"
        )

    product_id = fields.Many2one('product.product', 'Product', auto_join=True)
    location_id = fields.Many2one('stock.location', 'Location', auto_join=True)
    qty = fields.Float('Quantity')
    product_uom_id = fields.Many2one(related='product_id.uom_id')
    owner_id = fields.Many2one('res.partner', 'Owner')
    company_id = fields.Many2one('res.company', 'Company')
    reservation_id = fields.Many2one('stock.move', 'Reserved')
