from odoo import api, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _prepare_pack_ops(self, quants, forced_qties):
        """
        This method will add additional products on stock
        moves and pack operations.
        There are three main steps:
        1. Call super and retrieve the result
        2. Sum quantities by picking and product
        3. Create additional moves
        4. Valid (action_confirm) and assign moves (action_assign)
        5. Append additional pack operations values to result
        :param quants:
        :param forced_qties:
        :return:
        """
        self.ensure_one()

        ######################
        # Step 1: Call super #
        ######################
        result = \
            super(StockPicking, self)._prepare_pack_ops(quants, forced_qties)

        product_obj = self.env['product.product']

        ##########################
        # Step 2: Sum quantities #
        ##########################
        values = {}
        for pack_operation in result:
            if 'product_id' not in pack_operation \
                    or 'picking_id' not in pack_operation:
                return result
            product_id = pack_operation['product_id']
            picking_id = pack_operation['picking_id']

            pack_operation_qty = pack_operation.get('product_qty', 0)
            pack_operation_uom_id = pack_operation.get('product_uom_id')

            picking_values = values.get(picking_id, {})
            product_values = picking_values.get(product_id)
            if not product_values:
                product = product_obj.browse(product_id)
                product_uom_id = product.uom_id.id
                current_qty = 0
            else:
                product_uom_id = product_values['product_uom_id']
                current_qty = product_values['product_qty']

            if pack_operation_uom_id != product_uom_id:
                pack_operation_uom = self.env['product.uom'].browse(
                    pack_operation_uom_id)
                pack_operation_qty = pack_operation_uom._compute_quantity(
                    pack_operation_qty,
                    product_uom_id
                )
            product_qty = current_qty + pack_operation_qty

            product_values = {
                'product_qty': product_qty,
                'product_uom_id': product_uom_id
            }
            picking_values[product_id] = product_values
            values[picking_id] = picking_values

        ###################################
        # Step 3: Create additional moves #
        ###################################
        for picking_id, products in values.iteritems():
            picking = self.browse(picking_id)
            additional_moves = self.env['stock.move']

            for product_id, product_values in products.iteritems():
                product = product_obj.browse(product_id)
                product_qty = product_values['product_qty']

                if not product.additional_product_id:
                    continue
                additional_product_tmpl = product.additional_product_id

                if len(additional_product_tmpl.product_variant_ids) != 1:
                    raise UserError(
                        _('The product %s can only have one variant'
                          % additional_product_tmpl.name))
                additional_product = \
                    additional_product_tmpl.product_variant_ids[0]

                add_product_uom = additional_product.uom_id
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

                move_vals = {
                    'name': product.display_name,
                    'sequence': 9999,
                    'product_id': additional_product.id,
                    'product_uom_qty': add_product_qty,
                    'product_uom': add_product_uom.id,
                    'partner_id': picking.partner_id.id,
                    'location_id': picking.location_id.id,
                    'location_dest_id': picking.location_dest_id.id,
                    'picking_id': picking.id,
                    'origin': picking.name,
                }
                additional_moves |= additional_moves.create(move_vals)

            ##################################
            # Step 4: Valid and assign moves #
            ##################################
            additional_moves.action_confirm()
            additional_moves.action_assign(no_prepare=True)
            additional_quants = additional_moves.mapped('reserved_quant_ids')

            ###################################################
            # Step 5: Append pack operations values to result #
            ###################################################
            additional_result = super(StockPicking, picking).\
                _prepare_pack_ops(additional_quants, {})
            for line in additional_result:
                line['is_additional_line'] = True

            result += additional_result

        return result
