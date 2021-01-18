# -*- coding: utf-8 -*-
# © 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    qty_backorder = fields.Integer(
        "Nbr Backorder",
        help="Quantity of customers having a picking waiting for the "
        "availability of product",
        readonly=True,
    )


class StockPicking(models.Model):
    _inherit = "stock.picking"

    qty_outofstock = fields.Integer(
        "Nbr Out of Stock", help="Quantity of products where the available stock is < 0"
    )

    qty_backorder = fields.Integer(
        "Nbr Backorder",
        help="Quantity of deliveries part of a delivery round waiting for "
        "availability. For each product of the reception order, we "
        "count the customers (delivery address) waiting for the goods "
        "and we sum those quantities",
    )

    @api.model
    def create(self, vals):
        record = super(StockPicking, self).create(vals)
        if "grn_id" in vals:
            record.button_priority_recompute()
        return record

    @api.multi
    def write(self, vals):
        result = super(StockPicking, self).write(vals)
        if "grn_id" in vals:
            self.button_priority_recompute()
        return result

    @api.multi
    def _compute_qty_backorder(self):
        """ Amount of move lines having a backorder """
        # The computation is performed with 1 query per warehouse
        receptions = {}  # receptions grouped by warehouse stock location
        for record in self:
            if record.location_id.usage != "supplier":
                # restrict this computation to receptions only
                record.qty_backorder = 0
            else:
                stock_loc = record.picking_type_id.warehouse_id.lot_stock_id
                receptions.setdefault(stock_loc.id, self.browse())
                receptions[stock_loc.id] += record
        # Now compute the qty
        for stock_id, pickings in receptions.iteritems():
            # We count the number of moves from stock in
            # state == confirmed("Waiting Availability")
            # for each product
            # part of a delivery round
            # Each delivery address count for 1
            _logger.debug("Computing qty_backorder")

            packs = pickings.mapped("pack_operation_product_ids")
            all_products = packs.mapped("product_id")
            if not all_products:
                continue

            self._cr.execute(
                """
                WITH moves AS (
                    SELECT distinct move.partner_id, move.product_id
                    FROM stock_move AS move
                    LEFT JOIN stock_location AS loc
                        ON move.location_id = loc.id
                    JOIN stock_location p ON p.parent_left<=loc.parent_left
                        AND p.parent_right>=loc.parent_right
                    JOIN stock_picking AS picking
                        ON picking.id = move.picking_id
                    WHERE move.state = 'confirmed'
                    AND picking.delivery_round_id IS NOT NULL
                    AND move.product_id in %s
                    AND p.id = %s
                ),
                quantity AS (
                    SELECT product_id, count(*) as count
                    FROM moves
                    GROUP BY product_id
                )
                UPDATE stock_pack_operation SET qty_backorder = (
                    SELECT count FROM quantity
                    WHERE stock_pack_operation.product_id=quantity.product_id
                    )
                WHERE id in %s
                """,
                (tuple(all_products.ids), stock_id, tuple(packs.ids)),
            )

            # self._cr.execute("""
            #     UPDATE stock_picking SET qty_backorder = (
            #         SELECT sum(qty_backorder)
            #         FROM stock_pack_operation
            #         WHERE stock_pack_operation.picking_id = stock_picking.id
            #         )
            #     WHERE id in %s
            #     """, (tuple(pickings.ids), ))

            for record in pickings:
                record.qty_backorder = sum(
                    record.mapped("pack_operation_product_ids.qty_backorder")
                )
            _logger.debug("Computing qty_backorder - done")

    @api.multi
    def _compute_qty_outofstock(self):
        _logger.debug("Computing qty_outofstock")
        all_products = self.mapped("pack_operation_product_ids.product_id")
        products_unavailable_ids = set(
            all_products.filtered(lambda r: r.immediately_usable_qty < 0).ids
        )
        for record in self:
            product_ids = set(
                record.mapped("pack_operation_product_ids").mapped("product_id").ids
            )
            record.qty_outofstock = len(
                product_ids.intersection(products_unavailable_ids)
            )
        _logger.debug("Computing qty_outofstock - done")

    def _calc_priority(self):
        return self.qty_backorder * 1000 + self.qty_outofstock

    @api.multi
    def button_priority_recompute(self):
        res = super(StockPicking, self).button_priority_recompute()
        receptions = self.filtered(lambda r: r.location_id.usage == "supplier")
        receptions._compute_qty_backorder()
        receptions._compute_qty_outofstock()
        for record in receptions:
            record.rank = record._calc_priority()
        return res

    @api.model
    def _cron_priority_recompute(self):
        domain = [
            ("grn_id", "!=", False),
            ("state", "in", ("assigned", "partially_available")),
        ]
        receptions = self.search(domain)
        receptions._compute_qty_backorder()
        receptions._compute_qty_outofstock()
        for picking in receptions:
            priority = picking._calc_priority()
            if picking.rank != priority:
                picking.rank = priority
