# © 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields

from odoo.addons.alc_stock_picking_rank.models.stock_picking import (
    StockPicking as StockPickingBase,
)

_logger = logging.getLogger(__name__)


class StockPicking(StockPickingBase):

    count_partners_waiting_for_reception = fields.Integer(
        "Nbr partner waiting for this reception",
        help="Count of deliveries waiting for availability of one the incoming "
        "products. For each product of the reception order, we "
        "count the customers (delivery address) waiting for the goods "
        "and we sum those quantities",
    )
    count_products_waiting_for_reception = fields.Integer(
        "Nbr products Out of Stock", help="Count of products waiting for availability."
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.filtered("grn_id").button_rank_recompute()
        return records

    def write(self, vals):
        result = super().write(vals)
        if "grn_id" in vals:
            self.button_rank_recompute()
        return result

    def _compute_waiting_for_reception(self):
        """Compute the waiting for reception fields for the given pickings."""
        # The computation is performed with 1 query per warehouse
        self.flush_recordset()
        receptions = {}  # receptions grouped by warehouse stock location
        for record in self:
            if record.location_id.usage == "supplier":
                stock_loc = record.picking_type_id.warehouse_id.lot_stock_id
                receptions.setdefault(stock_loc.id, self.browse())
                receptions[stock_loc.id] += record
        # Now compute the qty
        for stock_id, pickings in receptions.items():
            # We count the number of moves from stock in
            # state == confirmed("Waiting Availability")
            # for each product
            # part of a delivery round
            # Each delivery address count for 1
            _logger.debug("Computing qty_backorder")
            self.env.cr.execute(
                """
                CREATE TEMPORARY TABLE outgoing_moves AS (
                    SELECT
                        distinct outgoing_move.partner_id AS partner_id,
                        outgoing_move.product_id AS product_id,
                        incoming_move.picking_id AS picking_id
                    FROM stock_move AS outgoing_move
                    JOIN stock_location AS loc
                        ON outgoing_move.location_id = loc.id
                    JOIN stock_location dest_loc
                        ON outgoing_move.location_dest_id = dest_loc.id
                        AND dest_loc.usage = 'customer'
                    JOIN stock_location p ON
                        p.id = %(stock_id)s
                        AND loc.parent_path like p.parent_path || '%%'
                    JOIN stock_picking AS picking
                        ON picking.id = outgoing_move.picking_id
                    JOIN stock_move AS incoming_move
                        ON incoming_move.picking_id in %(picking_ids)s
                        AND incoming_move.product_id = outgoing_move.product_id
                    WHERE
                        outgoing_move.state in ('confirmed', 'partially_available')
                );
                -- reset the stock_move_line count_partners_waiting_for_reception
                UPDATE
                    stock_move_line
                SET
                    count_partners_waiting_for_reception = 0
                WHERE picking_id in %(picking_ids)s;

                -- set the stock_move_line count_partners_waiting_for_reception for
                -- each product found in the outgoing_moves table
                UPDATE
                    stock_move_line
                SET
                    count_partners_waiting_for_reception = line_waiting.count
                FROM
                    (
                        SELECT count(partner_id) as count, product_id FROM outgoing_moves
                        GROUP BY product_id
                    ) as line_waiting
                WHERE picking_id in %(picking_ids)s and stock_move_line.product_id = line_waiting.product_id;

                -- reset the stock_picking count_partners_waiting_for_reception and
                -- count_products_waiting_for_reception
                UPDATE
                    stock_picking
                SET
                    count_products_waiting_for_reception = 0,
                    count_partners_waiting_for_reception = 0
                WHERE id in %(picking_ids)s;

                -- set the stock_picking count_partners_waiting_for_reception and
                -- count_products_waiting_for_reception for each picking found in the
                -- outgoing_moves table
                UPDATE
                    stock_picking
                SET
                    count_products_waiting_for_reception = line_waiting.products_count,
                    count_partners_waiting_for_reception = line_waiting.partners_count
                FROM
                    (
                        SELECT
                            count(distinct product_id) as products_count,
                            count(distinct partner_id) as partners_count,
                            picking_id
                        FROM outgoing_moves
                        GROUP BY picking_id
                    ) as line_waiting
                WHERE id = line_waiting.picking_id;

                DROP TABLE outgoing_moves;
                """,
                {"stock_id": stock_id, "picking_ids": tuple(pickings.ids)},
            )

            pickings.invalidate_recordset(
                [
                    "count_products_waiting_for_reception",
                    "count_partners_waiting_for_reception",
                ]
            )
            pickings.move_line_ids.invalidate_recordset(
                ["count_partners_waiting_for_reception"]
            )

        _logger.debug("Computing qty_backorder - done")

    def _calc_reception_rank(self):
        """Compute the rank of the given receptions."""
        for record in self:
            rank = (
                record.count_partners_waiting_for_reception * 1000
                + record.count_products_waiting_for_reception
            )
            if record.rank != rank:
                record.rank = rank

    def button_rank_recompute(self):
        res = super().button_rank_recompute()
        receptions = self.filtered(lambda r: r.location_id.usage == "supplier")
        receptions._compute_waiting_for_reception()
        receptions._calc_reception_rank()
        return res

    @api.model
    def _cron_reception_rank_recompute(self):
        domain = [
            ("grn_id", "!=", False),
            ("state", "in", ("assigned", "confirmed")),
        ]
        receptions = self.search(domain)
        receptions.button_rank_recompute()
