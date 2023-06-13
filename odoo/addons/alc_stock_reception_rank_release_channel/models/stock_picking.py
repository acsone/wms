# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_stock_reception_rank.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):
    def _calc_reception_rank(self):
        """Compute the rank of the given receptions."""
        res = super()._calc_reception_rank()
        receptions_with_rank = self.filtered(lambda r: r.rank > 0)
        if not receptions_with_rank:
            return res
        self.env.cr.execute(
            """
            -- Select the receptions picking_id where products are
            -- part confirmed or partially available outgoing pickings
            -- and the picking is linked to a release channel
            -- we count the number of release channel by picking_id

            SELECT
                incoming_move.picking_id,
                count(distinct outgoing_picking.release_channel_id)
            FROM
                stock_move incoming_move
            JOIN
                stock_move outgoing_move
                ON incoming_move.product_id = outgoing_move.product_id
            JOIN
                stock_picking outgoing_picking
                ON outgoing_move.picking_id = outgoing_picking.id
            JOIN stock_location dest_loc
                ON outgoing_move.location_dest_id = dest_loc.id
            WHERE
                incoming_move.picking_id in %(picking_ids)s
                AND dest_loc.usage = 'customer'
                AND outgoing_picking.release_channel_id is not null
                AND outgoing_move.state in ('confirmed', 'partially_available')
            GROUP BY
                incoming_move.picking_id

        """,
            {"picking_ids": tuple(receptions_with_rank.ids)},
        )
        for picking_id, count_release_channel in self.env.cr.fetchall():
            receptions_with_rank.browse(picking_id).rank += (
                count_release_channel * 1000000
            )
        return res
