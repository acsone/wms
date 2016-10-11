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

from datetime import date

from openerp import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    arrangement_importance = fields.Float(
        'Arrangement Importance',
        compute='_get_arrangement_importance')

    @api.one
    def _get_arrangement_importance(self):
        # il faut calculer combien de temps on tient en tenant compte d'une consommation moyenne de 1,6 (=2)
        """ How often the product is taken in a bin, how important it is to
        arrange. This is divided by the quantity already arranged. """
        start_date = (date.today() - timedelta(days=6 * 30)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        customer_loc = self.env.ref('stock.stock_location_customers')
        qty_moves = self.env['stock.move'].search_count([
            ('date', '>=', start_date),
            ('product_id', '=', self.id),
            ('state', 'not in', ('draft', 'cancel')),
            ('location_dest_id', '=', customer_loc.id),
            ])
        # FIXME - Hugly: Parking string hardcoded
        qty_in_stock = (self.qty_available -
                        self.with_context(location="Parking").qty_available)

        self.arrangement_importance = qty_moves / max(1, self.qty_in_stock)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    qty_outofstock = fields.Integer(
        'Qty Out of Stock',
        compute='_get_qty_backorder')

    qty_backorder = fields.Integer(
        'Qty Backorder',
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

    @api.model
    def _cron_priority_recompute(self):
        domain = [
            ('grn_id', '!=', False),
            ('state', 'in', ('assigned', 'partially_available'))]
        for picking in self.search(domain):
            priority = picking._calc_priority()
            if picking.sequence != priority:
                picking.sequence = priority
