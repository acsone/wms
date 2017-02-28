# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_line_original = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='order_id',
        compute='_compute_order_lines',
        readonly=False,
        store=False,
        string='Original lines',
    )

    order_line_additional = fields.One2many(
        comodel_name='sale.order.line',
        inverse_name='order_id',
        compute='_compute_order_lines',
        readonly=True,
        store=False,
        string='Additional lines',
    )
    order_line_additional_count = fields.Integer(
        compute='_compute_order_line_additional_count',
        readonly=True,
        store=False,
        string='Additional lines count',
    )

    @api.onchange('order_line_additional')
    @api.depends('order_line_additional')
    def _compute_order_line_additional_count(self):
        for order in self:
            count = len(order.order_line_additional)
            order.order_line_additional_count = count

    @api.depends('order_line')
    def _compute_order_lines(self):
        for order in self:
            order_line_original = order.order_line.filtered(
                lambda l: not l.additional_line
            )
            order_line_additional = order.order_line.filtered(
                lambda l: l.additional_line
            )
            order.update({
                'order_line_original': order_line_original,
                'order_line_additional': order_line_additional,
            })

    @api.onchange('order_line_original')
    def _onchange_order_line_original(self):
        # Compute additional lines
        order_line_additional = []

        order_lines = self.order_line_original.filtered(
            lambda l: not l.additional_line
        )
        for line in order_lines:
            product_uom_qty = line.product_uom_qty
            for additional_product in line.product_id.additional_product_ids:
                original_quantity = additional_product.original_quantity
                if product_uom_qty >= original_quantity:
                    new_template = additional_product.product_id
                    new_product = new_template.product_variant_ids[0]
                    method = additional_product.calculation_method
                    if method == 'once':
                        new_quantity = additional_product.quantity
                    elif method == 'proportional':
                        factor = int(product_uom_qty/original_quantity)
                        new_quantity = additional_product.quantity * factor

                    position = additional_product.position_on_sale
                    values = {
                        'product_id': new_product.id,
                        'product_uom_qty': new_quantity,
                        'additional_line': True,
                        'additional_line_is_free': additional_product.is_free,
                        'additional_line_position': position,
                        'additional_line_parent_sequence': line.sequence,
                    }
                    order_line_additional.append((0, 0, values))
        self.update({
            'order_line_additional': order_line_additional
        })
        for line in self.order_line_additional:
            line.product_id_change()
            if line.additional_line_is_free:
                line.price_unit = 0.0

        # Compute final order lines
        sequence = 1

        at_end_lines = []
        for line_original in self.order_line_original.sorted(
            key=lambda l: l.sequence
        ):
            original_sequence = line_original.sequence
            line_original.sequence = sequence
            sequence += 1
            for line_add in self.order_line_additional.sorted(
                key=lambda l: l.sequence
            ):
                parent_sequence = line_add.additional_line_parent_sequence
                if parent_sequence == original_sequence:
                    if line_add.additional_line_position == 'just_after':
                        line_add.sequence = sequence
                        sequence += 1
                    elif line_add.additional_line_position == 'at_end':
                        at_end_lines.append(line_add)
        for line in at_end_lines:
            line.sequence = sequence
            sequence += 1

        self.update({
            'order_line': (
                self.order_line_original + self.order_line_additional
            ).sorted(key=lambda l: l.sequence)
        })

    def fields_view_get(self, cr, user, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """ To use the same views of order line
        for original and additional order lines """
        res = super(SaleOrder, self).fields_view_get(
            cr, user, view_id=view_id, view_type=view_type,
            context=context, toolbar=toolbar, submenu=submenu
        )
        if res['type'] == 'form':
            views = res['fields']['order_line']['views']
            res['fields']['order_line_original']['views'] = views
            res['fields']['order_line_additional']['views'] = views
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    additional_line = fields.Boolean(
        string='Additional line'
    )
    additional_line_is_free = fields.Boolean(
        string='Additional line is free'
    )
    additional_line_position = fields.Char(
        string='Additional line position'
    )
    additional_line_parent_sequence = fields.Integer(
        string='Additional line parent sequence'
    )
