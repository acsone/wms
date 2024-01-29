# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import fields, models, tools

from odoo.addons.base.models.res_users import Users
from odoo.addons.stock.models.stock_location import Location
from odoo.addons.stock.models.stock_picking import Picking


class AlcStockMoveLineAudit(models.Model):

    _name = "alc.stock.move.line.audit"
    _description = "User operations Audit"

    _auto = False

    date = fields.Datetime(readonly=True)
    qty_done = fields.Float(readonly=True)
    picking_destination_location_id = fields.Many2one[Location](
        related="picking_id.location_dest_id", readonly=True
    )
    picking_id = fields.Many2one[Picking](readonly=True)
    user_id = fields.Many2one[Users](readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
                SELECT
                  sml.id,
                  sp.date_done as date,
                  sml.qty_done,
                  sp.location_dest_id as picking_destination_location_id,
                  sp.id as picking_id,
                  sp.user_id
                FROM
                    stock_move_line sml
                JOIN
                    stock_picking sp
                    ON sp.id = sml.picking_id
            """
        self.env.cr.execute(
            "CREATE OR REPLACE VIEW %s AS (%s)", (AsIs(self._table), AsIs(query))
        )
