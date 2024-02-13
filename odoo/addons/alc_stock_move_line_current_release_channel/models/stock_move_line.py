# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.osv.expression import FALSE_DOMAIN, NEGATIVE_TERM_OPERATORS

from odoo.addons.stock.models.stock_move_line import StockMoveLine as StockMoveLineBase


class StockMoveLine(StockMoveLineBase):

    current_release_channel = fields.Boolean(
        compute="_compute_current_release_channel",
        search="_search_current_release_channel",
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
                            JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
                            WHERE spt.code = 'outgoing'
                            AND sp.release_channel_id IS NOT NULL
                            AND sm.product_id = sml.product_id
                            AND sm.state = 'waiting'
                            AND sml.state = 'assigned'
                    )
                AND id IN %(ids)s
        """
        self.env.cr.execute(query, {"ids": tuple(self.ids)})
        result_ids = self.env.cr.fetchall()
        for line in self:
            line.current_release_channel = bool(
                line.id in [result[0] for result in result_ids]
            )

    def _search_current_release_channel(self, operator, value):
        """
        Search only for the True values as retrieved records could be huge.

        This will retrieve the lines for moves that:

            - Are for OUT pickings
            - Have the same product
            - Have a release channel affected
            - Are waiting (indeed, the OUT moves are waiting for stock quantities that should be refilled)
            - The lines should be assigned as it should correspond to available refill moves
        """
        if (operator not in NEGATIVE_TERM_OPERATORS and value) or (
            operator in NEGATIVE_TERM_OPERATORS and not value
        ):
            query = """
                SELECT id
                    FROM stock_move_line sml
                        WHERE EXISTS(
                            SELECT 1 FROM stock_move sm
                                JOIN stock_picking sp ON sp.id = sm.picking_id
                                JOIN stock_picking_type spt ON spt.id = sp.picking_type_id
                                WHERE spt.code = 'outgoing'
                                AND sp.release_channel_id IS NOT NULL
                                AND sm.product_id = sml.product_id
                                AND sm.state = 'waiting' -- Take only out moves that are waiting for quantities
                                AND sml.state = 'assigned'  -- Take only moves that can fullfill quantities (e.g. Refill ones)
                        )
            """
            self.env.cr.execute(query)
            results = self.env.cr.fetchall()
            return [("id", "in", [result[0] for result in results])]
        return FALSE_DOMAIN
