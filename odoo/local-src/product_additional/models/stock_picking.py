# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_prepare_partial(self):
        result = super(StockPicking, self).do_prepare_partial()

        PackOperation = self.env['stock.pack.operation']

        for picking in self:
            additional_moves = self.env['stock.move']
            qty_by_product = {}

            ##########################
            # Step 2: Sum quantities #
            ##########################
            for operation in picking.pack_operation_ids:
                product = qty_by_product.get(operation.product_id, 0)
                product += operation.product_qty
                qty_by_product[operation.product_id] = product

            ###################################
            # Step 3: Create additional moves #
            ###################################
            for product, product_qty in qty_by_product.iteritems():
                if not product.additional_product_id:
                    continue
                additional_product = product.additional_product_id

                ratio_main_product = product.ratio_main_product
                ratio_additional_product = product.ratio_additional_product

                coefficient = int(product_qty / ratio_main_product)
                add_product_qty = coefficient * ratio_additional_product
                if not add_product_qty:
                    continue

                # Check the qty available
                # If the quantity available is equal to zero we ignore this
                # additional product
                qty_available = additional_product.immediately_usable_qty
                if not qty_available:
                    continue
                # If the quantity available is less than the additional
                # product quantity we take only the quantity available
                if add_product_qty > qty_available:
                    add_product_qty = qty_available

                main_moves = \
                    operation.mapped('linked_move_operation_ids.move_id')

                move_vals = {
                    'name': product.display_name,
                    'sequence': 9999,
                    'product_id': additional_product.id,
                    'product_uom_qty': add_product_qty,
                    'product_uom': additional_product.uom_id.id,
                    'partner_id': picking.partner_id.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                    'picking_id': picking.id,
                    'origin': picking.name,
                }
                additional_move = additional_moves.create(move_vals)

                main_moves.write({
                    'additional_move_ids': [(4, additional_move.id, 0)],
                })

                additional_moves |= additional_move

            if not additional_moves:
                return result

            ##################################
            # Step 4: Valid and assign moves #
            ##################################
            additional_moves.action_confirm()
            additional_moves.action_assign(no_prepare=True)
            additional_quants = additional_moves.mapped('reserved_quant_ids')

            ###################################################
            # Step 5: Append pack operations values to result #
            ###################################################
            additional_packs = picking._prepare_pack_ops(additional_quants, {})
            for vals in additional_packs:
                vals['fresh_record'] = False
                vals['is_additional_line'] = True
                PackOperation |= PackOperation.create(vals)

        return result
