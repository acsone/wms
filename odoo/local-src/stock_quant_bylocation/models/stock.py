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

from openerp import fields, models, tools


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
            "groupby": "product_id, location_id, owner_id, company_id, "
                       "reservation_id"
            }

    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
        CREATE OR REPLACE VIEW """ + self._table + """ AS (
        SELECT %(select)s
        FROM stock_quant quant
        LEFT join product_product product ON quant.product_id=product.id
        WHERE qty >= 0
        GROUP BY %(groupby)s
        )
        """ % self._prepare_init())

    product_id = fields.Many2one(
        'product.product', 'Product',
        auto_join=True)
    location_id = fields.Many2one(
        'stock.location', 'Location',
        auto_join=True)
    qty = fields.Float(
        'Quantity')
    product_uom_id = fields.Many2one(
        related='product_id.uom_id')
    owner_id = fields.Many2one(
        'res.partner', 'Owner')
    company_id = fields.Many2one(
        'res.company', 'Company')
    reservation_id = fields.Many2one(
        'stock.move', 'Reserved')
