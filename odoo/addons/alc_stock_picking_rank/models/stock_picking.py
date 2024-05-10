# Copyright 2016 BCIM sprl, Camptocamp
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import fields
from odoo.tools import sql

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    _order = "priority desc, rank desc, date asc, id desc"

    rank = fields.Float(
        "Rank",
        digits=(12, 0),
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
        copy=False,
    )

    def init(self):  # pylint: disable=missing-return
        super().init()
        # if column rank already exists and is not a numeric column, convert it to numeric
        self.env.cr.execute(
            "SELECT column_name, data_type "
            "FROM information_schema.columns "
            "WHERE table_name = %s AND column_name = %s",
            (self._table, "rank"),
        )
        res = self.env.cr.fetchone()
        if res and res[1] != "numeric":
            self.env.cr.execute(
                "ALTER TABLE %s ALTER COLUMN rank TYPE numeric", (AsIs(self._table),)
            )

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

        # add default value for rank column definition if not exists
        # check definition of rank column
        self.env.cr.execute(
            "SELECT column_default "
            "FROM information_schema.columns "
            "WHERE table_name = %s AND column_name = %s",
            (self._table, "rank"),
        )
        res = self.env.cr.fetchone()
        if res[0] is None:
            # add default value for rank column to avoid error on sort with null value
            # set first
            self.env.cr.execute(
                "ALTER TABLE %s ALTER COLUMN rank SET DEFAULT 0", (AsIs(self._table),)
            )
            self.env.cr.execute(
                "update %s set rank = 0 where rank is null", (AsIs(self._table),)
            )

    def button_rank_recompute(self):
        pass
