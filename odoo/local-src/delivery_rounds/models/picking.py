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

from openerp import api, fields, models, _
from openerp.exceptions import Warning


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_round_id = fields.Many2one(
        'round.instance', 'Delivery Round')
    delivery_round_state = fields.Selection(
        related='delivery_round_id.state',
        store=True,
        string="Delivery Round State")

    number_of_drug = fields.Float('Number of medical products',
                                       compute='_compute_number_of_products')
    number_of_cold = fields.Float('Number of cold products',
                                    compute='_compute_number_of_products')
    number_of_food = fields.Float('Number of food products',
                                    compute='_compute_number_of_products')
    number_of_human_food = fields.Float(
        'Number of human food',
        compute='_compute_number_of_products')
    number_of_equipment = fields.Float(
        'Number of equipments',
        compute='_compute_number_of_products')
    number_total = fields.Float('Number of products',
                                  compute='_compute_number_of_products')

    @api.depends('move_lines',
                 'move_lines.product_id',
                 'move_lines.product_uom_qty')
    def _compute_number_of_products(self):
        for picking in self:
            number_of_drug = 0
            number_of_cold = 0
            number_of_food = 0
            number_of_human_food = 0
            number_of_equipment = 0
            number_total = 0

            for line in picking.move_lines:
                qty = line.product_uom_qty
                number_total += qty

                if not line.product_id or not line.product_id.categ_id:
                    continue
                categ = line.product_id.categ_id

                main_categ = self.env.ref('product.product_category_all')
                equipment_categ = \
                    self.env.ref('__setup__.product_categ_materiel')
                food_categ = self.env.ref('__setup__.product_categ_ali')
                drug_categ = self.env.ref('__setup__.product_categ_medoc')
                fridge_categ = self.env.ref('__setup__.product_categ_frigo')
                human_categ = self.env.ref('__setup__.product_categ_humain')

                # We need to have the main product category of the product
                # Equipment, Food, Drug, Fridge, Human drug
                while categ.parent_id and categ.parent_id != main_categ:
                    # The human drug category is a sub category of drug.
                    if categ == human_categ:
                        break
                    categ = categ.parent_id

                if categ == drug_categ:
                    number_of_drug += qty
                elif categ == fridge_categ:
                    number_of_cold += qty
                elif categ == food_categ:
                    number_of_food += qty
                elif categ == equipment_categ:
                    number_of_equipment += qty
                elif categ == human_categ:
                   number_of_human_food += qty

            picking.number_of_drug = number_of_drug
            picking.number_of_cold = number_of_cold
            picking.number_of_food = number_of_food
            picking.number_of_human_food = number_of_human_food
            picking.number_of_equipment = number_of_equipment
            picking.number_total = number_total

    def _get_all_from_pickings(self):
        res = set()

        def _rec_add(moves):
            res.update([move.id for move in moves])
            for move in moves:
                _rec_add(move.move_orig_ids)

        for picking in self:
            moves = picking.move_lines
            _rec_add(moves)
        return self.env['stock.move'].browse(list(res)).mapped('picking_id')

    def _get_all_dest_pickings(self):
        res = set()

        def _rec_add(moves):
            res.update([move.id for move in moves])
            for move in moves:
                if move.move_dest_id:
                    _rec_add([move.move_dest_id])

        for picking in self:
            moves = picking.move_lines
            _rec_add(moves)
        return self.env['stock.move'].browse(list(res)).mapped('picking_id')

    @api.multi
    def write(self, vals):
        if (self and 'delivery_round_id' in vals and
                not self._context.get('noround_write')):
            # propagate to delivery when a picking is (un)assigned to a
            # delivery round
            shippings = self._get_all_dest_pickings().filtered(
                lambda r: r.picking_type_code == 'outgoing')
            # ensure all related pickings are assigned to the same delivery
            # round
            pickings = shippings._get_all_from_pickings()
            # TODO: we should ensure a picking is not already done for another
            #       delivery round
            pickings = pickings
            pickings = pickings.filtered(
                lambda r: r.state in (
                    'waiting',
                    'confirmed',
                    'partially_available',
                    'assigned') and
                r.delivery_round_id.id != vals['delivery_round_id'])
            # if not pickings:
            #     raise Warning(_(
            #         'No available picking to assign this delivery round'))
            if pickings:
                pickings.with_context(noround_write=True).write(
                    {'delivery_round_id': vals['delivery_round_id']})
            del vals['delivery_round_id']
        if not vals:
            return True
        return super(StockPicking, self).write(vals)

    @api.model
    def _group_delivery_round(self, ids, domain, **kwargs):
        vehicle = self.env['round.instance'].search(
            [('state', 'in', ('draft', ))]).name_get()
        return vehicle, None

    _group_by_full = {
        'delivery_round_id': _group_delivery_round,
    }

    @api.multi
    def button_delivery_round(self):
        return dict(self.env.ref(
            'delivery_rounds.action_picking_assign_delivery_round').read()[0])


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    def get_action_picking_tree_ready(self):
        """ Add filter for 'To Do' picking from dashboard to activate a filter
        to display only pickings linked to open delivery round """
        res = super(StockPickingType, self).get_action_picking_tree_ready()
        if self.subcode == 'PICK':
            res['context'] = res['context'].replace(
                ',', ", 'search_default_delivery_round_state': 'open', ", 1)
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if vals.get('picking_id'):
            # when a picking is assigned to a move, we have to ensure the whole
            # group (all dest moves) has the same delivery round
            # Check delivery round on orig moves as picking assignment is
            # performed from pick to ship
            orig_drs = self.mapped('move_orig_ids').mapped(
                'picking_id.delivery_round_id')
            if len(orig_drs) > 1:
                raise Warning(_('Source moves have different delivery round. '
                                'Please fix manually'))
            for orig_dr in orig_drs:
                picking = self.env['stock.picking'].browse(
                    vals.get('picking_id'))
                if picking.delivery_round_id != orig_dr:
                    picking.delivery_round_id = orig_dr.id
        return res
