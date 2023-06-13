# Copyright 2016 BCIM sprl, Camptocamp
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tools import sql

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    _order = "priority desc, rank desc, date asc, id desc"

    rank = fields.Integer(
        "Rank",
        default=-1,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
    )

    def init(self):

        index_name = "stock_picking_order_list_sort_desc_index"
        sql.create_index(
            self.env.cr,
            index_name,
            self._table,
            ["priority desc", "rank desc", "date asc", "id desc"],
        )
        index_name = "stock_picking_order_list_sort_desc_index_2"
        sql.create_index(
            self.env.cr,
            index_name,
            self._table,
            ["picking_type_id", "priority desc", "rank desc", "date asc", "id desc"],
        )

    def button_rank_recompute(self):
        pass
