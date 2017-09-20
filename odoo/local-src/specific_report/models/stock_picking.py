# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Sylvain Van Hoof <svh@sylvainvh.be>
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
from collections import defaultdict

from odoo import models, fields, api, _
from odoo.exceptions import Warning


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    number_of_drug = fields.Float(
        'Number of medical products',
        compute='_compute_number_of_products')
    number_of_cold = fields.Float(
        'Number of cold products',
        compute='_compute_number_of_products')
    number_of_food = fields.Float(
        'Number of food products',
        compute='_compute_number_of_products')
    number_of_human_food = fields.Float(
        'Number of human food',
        compute='_compute_number_of_products')
    number_of_equipment = fields.Float(
        'Number of equipments',
        compute='_compute_number_of_products')
    number_total = fields.Float(
        'Number of products',
        compute='_compute_number_of_products')

    item_number_of_drug = fields.Float(
        'Number item of medical products',
        compute='_compute_number_of_products')
    item_number_of_cold = fields.Float(
        'Number item of cold products',
        compute='_compute_number_of_products')
    item_number_of_food = fields.Float(
        'Number item of food products',
        compute='_compute_number_of_products')
    item_number_of_human_food = fields.Float(
        'Number item of human food',
        compute='_compute_number_of_products')
    item_number_of_equipment = fields.Float(
        'Number item of equipments',
        compute='_compute_number_of_products')
    item_number_total = fields.Float(
        'Number item of products',
        compute='_compute_number_of_products')

    @api.depends('move_lines',
                 'move_lines.product_id',
                 'move_lines.product_uom_qty')
    def _compute_number_of_products(self):
        type_human = self.env.ref('__setup__.stock_picking_type_humain')
        type_cold = self.env.ref('__setup__.stock_picking_type_froid')
        type_drug = self.env.ref('__setup__.stock_picking_type_medoc')
        type_food = self.env.ref('__setup__.stock_picking_type_ali')
        type_equipment = self.env.ref('__setup__.stock_picking_type_materiel')

        main_categ = self.env.ref('product.product_category_all')
        equipment_categ = self.env.ref('specific_data.product_categ_materiel')
        food_categ = self.env.ref('specific_data.product_categ_ali')
        drug_categ = self.env.ref('specific_data.product_categ_medoc')
        fridge_categ = self.env.ref('specific_data.product_categ_frigo')
        human_categ = self.env.ref('specific_data.product_categ_humain')

        # Check quantities for packages
        for picking in self:
            number_of_drug = 0
            number_of_cold = 0
            number_of_food = 0
            number_of_human_food = 0
            number_of_equipment = 0
            number_total = 0

            for operation in picking.pack_operation_pack_ids:
                if not operation.package_id.original_picking_type_id:
                    raise Warning(_('There is no original picking type on '
                                    'this operation.'))

                picking_type = operation.package_id.original_picking_type_id

                qty = operation.package_id.nbr_packages
                number_total += qty

                if picking_type == type_drug:
                    number_of_drug += qty
                elif picking_type == type_cold:
                    number_of_cold += qty
                elif picking_type == type_food:
                    number_of_food += qty
                elif picking_type == type_equipment:
                    number_of_equipment += qty
                elif picking_type == type_human:
                    number_of_human_food += qty
                else:
                    raise Warning(_('The picking type %s is not correct')
                                  % picking_type.name)

            picking.number_of_drug = number_of_drug
            picking.number_of_cold = number_of_cold
            picking.number_of_food = number_of_food
            picking.number_of_human_food = number_of_human_food
            picking.number_of_equipment = number_of_equipment
            picking.number_total = number_total

            item_number_of_drug = 0
            item_number_of_cold = 0
            item_number_of_food = 0
            item_number_of_human_food = 0
            item_number_of_equipment = 0
            item_number_total = 0

            # Check quantities for products without pack
            for operation in picking.pack_operation_product_ids:
                if not operation.product_id.categ_id:
                    raise Warning(_('There is no category on this product'))

                categ = operation.product_id.categ_id

                qty = operation.qty_done
                item_number_total += qty

                # We need to have the main product category of the product
                # Equipment, Food, Drug, Fridge, Human drug
                while categ.parent_id and categ.parent_id != main_categ:
                    # The human drug category is a sub category of drug.
                    if categ == human_categ:
                        break
                    categ = categ.parent_id

                if categ == drug_categ:
                    item_number_of_drug += qty
                elif categ == fridge_categ:
                    item_number_of_cold += qty
                elif categ == food_categ:
                    item_number_of_food += qty
                elif categ == equipment_categ:
                    item_number_of_equipment += qty
                elif categ == human_categ:
                    item_number_of_human_food += qty
                else:
                    raise Warning(_('The category %s is not valid')
                                  % categ.name)

            picking.item_number_of_drug = item_number_of_drug
            picking.item_number_of_cold = item_number_of_cold
            picking.item_number_of_food = item_number_of_food
            picking.item_number_of_human_food = item_number_of_human_food
            picking.item_number_of_equipment = item_number_of_equipment
            picking.item_number_total = item_number_total

    @api.multi
    def get_moves_by_order(self):
        self.ensure_one()

        moves_by_order = defaultdict(list)
        backorder_moves_by_order = defaultdict(list)
        result = []
        moves_witout_order = []
        backorder_moves_without_order = []
        for line in self.move_lines:
            if not line.order_id:
                moves_witout_order.append(line)
            else:
                moves_by_order[line.order_id].append(line)

        backorders = self.env['stock.picking']. \
            search([('backorder_id', '=', self.id)])
        for backorder in backorders:
            for line in backorder.move_lines:
                if not line.order_id:
                    backorder_moves_without_order.append(line)
                else:
                    backorder_moves_by_order[line.order_id].append(line)

        result_dict = {}
        for order, moves in moves_by_order.iteritems():
            result_dict[order] = [moves,
                                  backorder_moves_by_order.get(order, [])]

        if moves_witout_order:
            result.append((None,
                           (moves_witout_order, backorder_moves_without_order)
                           ))

        result.extend(
            sorted(result_dict.items(),
                   key=lambda picking: (picking[0][0].date_order,
                                        picking[0][0].id))
        )
        return result
