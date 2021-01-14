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
from psycopg2.extensions import AsIs

from odoo import api, fields, models


def create_index(cr, index_name, table, expression):
    cr.execute("SELECT indexname FROM pg_indexes WHERE indexname = %s", (index_name,))
    if not cr.fetchone():
        cr.execute(
            "CREATE INDEX %s " "ON %s %s",
            (AsIs(index_name), AsIs(table), AsIs(expression)),
        )


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = "priority desc, rank desc, date asc, id desc"

    rank = fields.Integer(
        "Rank",
        default=-1,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )

    @api.model_cr
    def init(self):

        # index for the default _order of stock.picking
        index_name = "stock_picking_order_list_sort_desc_index"
        create_index(
            self.env.cr,
            index_name,
            self._table,
            "(priority desc, rank desc, date asc, id desc)",
        )
        index_name = "stock_picking_order_list_sort_desc_index_2"
        create_index(
            self.env.cr,
            index_name,
            self._table,
            "(picking_type_id, priority desc, rank desc, date asc, id desc)",
        )

    @api.multi
    def button_priority_recompute(self):
        pass
