# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

import logging
_logger = logging.getLogger(__name__)


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    qty_backorder = fields.Integer(
        'Nbr Backorder',
        readonly=True)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    qty_outofstock = fields.Integer(
        'Nbr Out of Stock',
        compute='_get_qty_backorder',
        help="Quantity of operations having a product where the current stock "
             "is <= 0")

    qty_backorder = fields.Integer(
        'Nbr Backorder',
        compute='_get_qty_backorder',
        help="Quantity of deliveries waiting for availability. We take all "
             "deliveries waiting any of the products listed in the operations "
             "and we count each distinct delivery address")

    @api.multi
    def _get_qty_backorder(self):
        """ Amount of move lines having a backorder """
        # The computation is performed with 1 query per warehouse
        receptions = {}  # receptions grouped by warehouse stock location
        supplier_locs = [
            self.env.ref('stock.stock_location_suppliers'),
            # what about transit inter-warehouse?
        ]
        for record in self:
            if record.location_id not in supplier_locs:
                # restrict this computation to receptions only (moves from
                # suppliers)
                record.qty_backorder = 0
                record.qty_outofstock = 0
            else:
                receptions.setdefault(
                    record.picking_type_id.warehouse_id.lot_stock_id.id,
                    self.browse())
                receptions[record.picking_type_id.warehouse_id
                           .lot_stock_id.id] += record
        # Now compute the qty
        for stock_id, pickings in receptions.iteritems():
            packs = pickings.mapped('pack_operation_product_ids')
            all_products = packs.mapped('product_id')
            if not all_products:
                continue

            # We count the number of moves from stock in
            #   - "Waiting Availability" (MTS)
            # for each product
            # Each delivery address count for 1
            self._cr.execute("""
                WITH moves AS (
                    SELECT distinct move.partner_id, move.product_id
                    FROM stock_move AS move
                    LEFT JOIN stock_location AS loc
                        ON move.location_id = loc.id
                    JOIN stock_location p ON p.parent_left<=loc.parent_left
                        AND p.parent_right>=loc.parent_right
                    WHERE move.state = 'confirmed'
                    -- AND move.partner_id IS NOT NULL
                    AND move.product_id in %s
                    AND p.id = %s
                )
                SELECT product_id, count(*)
                FROM moves
                GROUP BY product_id
                """, (tuple(all_products.ids), stock_id))
            backorders = dict(self._cr.fetchall())

            for record in pickings:
                for packop in record.pack_operation_product_ids:
                    qty_backorder = backorders.get(packop.product_id.id, 0)
                    if packop.qty_backorder != qty_backorder:
                        packop.write({
                            'qty_backorder': backorders.get(
                                packop.product_id.id, 0),
                        })
                products = record.mapped('pack_operation_product_ids') \
                    .mapped('product_id')
                record.qty_backorder = sum([backorders.get(prod_id, 0)
                                           for prod_id in products.ids])
                record.qty_outofstock = len(products.filtered(
                        lambda r: r.qty_available <= 0))

    def _calc_priority(self):
        return self.qty_backorder * 1000 + self.qty_outofstock

    @api.multi
    @api.constrains('grn_id')
    def _update_rank_on_grn(self):
        for rec in self:
            if not rec.grn_id:
                rec.rank = 0
            elif not rec.rank:
                rec.rank = self._calc_priority()

    @api.multi
    def button_priority_recompute(self):
        super(StockPicking, self).button_priority_recompute()
        self._cron_priority_recompute()

    @api.model
    def _cron_priority_recompute(self):
        domain = [
            ('grn_id', '!=', False),
            ('state', 'in', ('assigned', 'partially_available'))]
        for picking in self.search(domain):
            priority = picking._calc_priority()
            if picking.rank != priority:
                picking.rank = priority
