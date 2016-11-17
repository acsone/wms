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

from openerp import fields, models, api


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    qty_backorder = fields.Integer(
        'Nbr Backorder',
        readonly=True)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    qty_outofstock = fields.Integer(
        'Nbr Out of Stock',
        compute='_get_qty_backorder')

    qty_backorder = fields.Integer(
        'Nbr Backorder',
        compute='_get_qty_backorder')

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

            # We count the number of moves from stock in "Waiting Availability"
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
                    WHERE move.state='confirmed'
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
    def write(self, vals):
        if 'grn_id' in vals and 'priority' not in vals:
            if not vals['grn_id']:
                vals['sequence'] = 0
            else:
                vals['sequence'] = self._calc_priority()
        return super(StockPicking, self).write(vals)

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
            if picking.sequence != priority:
                picking.sequence = priority
