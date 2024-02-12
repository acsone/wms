# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase


class StockMoveLine(StockMoveLineBase):

    current_release_channel = fields.Boolean(
        compute="_compute_current_release_channel",
        string="In a current release channel",
        help="This line has its product in a current release channel",
    )

    def _compute_current_release_channel(self):
        query = """
            SELECT id
                FROM stock_move_line sml
                    WHERE EXISTS(
                        SELECT 1 FROM stock_move sm
                            JOIN stock_picking sp ON sp.id = sm.picking_id
                            JOIN stock_location sl ON sl.id = sm.location_dest_id
                            WHERE sl.usage = 'customer'
                            AND sp.release_channel_id IS NOT NULL
                            AND product_id = sml.product_id
                            AND sm.state NOT IN ('cancel', 'done')
                    )
                AND id IN %(ids)s
        """
        self.env.cr.execute(query, {"ids": tuple(self.ids)})
        result_ids = self.env.cr.fetchall()
        for line in self:
            line.current_release_channel = bool(
                line.id in [result[0] for result in result_ids]
            )
