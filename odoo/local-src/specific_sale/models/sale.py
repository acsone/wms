# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp

from odoo import api, fields, models, _


class Sale(models.Model):
    _inherit = 'sale.order'

    sale_channel = fields.Selection([
        ('phone', 'Phone'),
        ('mail', 'Mail'),
        ('fax', 'Fax'),
    ])

    sale_channel_visible = fields.Boolean(
        compute='_compute_sale_channel_required'
    )

    @api.depends('team_id')
    def _compute_sale_channel_required(self):
        direct_team = self.env.ref('sales_team.team_sales_department')
        for record in self:
            if direct_team and record.team_id == direct_team:
                record.sale_channel_visible = True
            else:
                record.sale_channel_visible = False

    @api.onchange('team_id')
    def onchange_team_id(self):
        if self.sale_channel_visible and not self.sale_channel:
            self.sale_channel = 'phone'
        elif not self.sale_channel_visible:
            self.sale_channel = False

    @api.model
    def get_values_for_additional_line(
            self,
            new_product,
            new_quantity,
            additional_product,
            position,
            line
    ):
        values = super(Sale, self).get_values_for_additional_line(
            new_product,
            new_quantity,
            additional_product,
            position,
            line
        )
        line_model = self.env['sale.order.line']
        qty_unavailable = line_model.get_product_qty_unavailable(
            new_product,
            values['product_uom_qty'],
            line.state == 'sale',
            line.id
        )
        values['product_qty_unavailable'] = qty_unavailable

        return values

    @api.model
    def get_current_values_for_additional_line(self, current_line, line):
        current_values = super(
            Sale, self
        ).get_current_values_for_additional_line(current_line, line)
        qty_unavailable = current_line.product_qty_unavailable
        current_values['product_qty_unavailable'] = qty_unavailable
        return current_values

    @api.model
    def get_accepted_fields_for_order_line(self):
        """
            To define accepted fields
            to copy original lines into final lines.
        """
        return super(Sale, self).get_accepted_fields_for_order_line() + [
            'edited_supplier_promotion',
            'edited_alcyon_discount',
            'is_delivery',
        ]

    def _create_delivery_line(self, carrier, price_unit):
        super(Sale, self.with_context(
            create_original_line_too=True
        ))._create_delivery_line(carrier, price_unit)

    @api.multi
    def order_lines_layouted(self):
        self.ensure_one()
        report_pages = super(Sale, self).order_lines_layouted()

        pharmacy_category = self.env.ref('__setup__.product_categ_humain')
        pharmacy_lines = self.env['sale.order.line'].search([
            ('order_id', '=', self.id),
            ('product_id.categ_id', 'child_of', pharmacy_category.id),
        ]).sorted()

        cascade_category = self.env.ref('__setup__.product_categ_importation')
        cascade_lines = self.env['sale.order.line'].search([
            ('order_id', '=', self.id),
            ('product_id.categ_id', 'child_of', cascade_category.id),
        ]).sorted()

        new_report_pages = []
        for report_page_category in report_pages:
            new_values = []
            for report_page in report_page_category:
                new_lines = [
                    line
                    for line in report_page['lines']
                    if line.id not in pharmacy_lines.ids + cascade_lines.ids
                ]
                if new_lines:
                    new_values.append({
                        'name': report_page['name'],
                        'subtotal': report_page['subtotal'],
                        'pagebreak': report_page['pagebreak'],
                        'lines': new_lines
                    })
            if new_values:
                new_report_pages.append(new_values)
            else:
                new_report_pages.append([])
        if pharmacy_lines:
            pharmacist_name = (
                pharmacy_lines[0].order_id.partner_id.pharmacist_id.name
                if pharmacy_lines[0].order_id.partner_id.pharmacist_id
                else ''
            )
            new_report_pages[-1].append({
                'name_list': [
                    _(
                        u'Following human medicines ordered '
                        u'under your responsibility.'
                    ),
                    _(
                        u'This command is transferred on your behalf '
                        u'to the pharmacy '
                        u'which will ensure the delivery of medicines.'
                    ),
                    _(
                        u'The medicines will be delivered '
                        u'to you by our care upon receipt of these '
                        u'from the pharmacy'
                    ),
                    _(
                        u'For any problems related to this command, '
                        u'please contact the pharmacist.'
                    ),
                ],
                'subtotal': False,
                'pagebreak': False,
                'only_quantity': True,
                'line_additional_text':
                    _(
                        u'Article transferred to dispensing pharmacy: '
                        u'%s'
                    ) % pharmacist_name,
                'lines': pharmacy_lines
            })
        if cascade_lines:
            new_report_pages[-1].append({
                'name_list': [
                    _(
                        u'Imported medicines under your entire responsibility'
                    ),
                ],
                'subtotal': False,
                'pagebreak': False,
                'lines': cascade_lines
            })
        return new_report_pages


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    exception = fields.Char(
        compute='_compute_exception',
    )

    @api.depends('product_id', 'price_unit', 'price_subtotal')
    def _compute_exception(self):
        line_exceptions = self.env['exception.rule'].search(
            [
                ('rule_group', '=', 'sale'),
                ('model', '=', 'sale.order.line'),
            ],
            order='id'
        )

        for line in self:
            exception = ''
            if line.product_id:
                for rule in line_exceptions:
                    if self.env['sale.order']._rule_eval(rule, 'line', line):
                        exception = rule.description
                        break
            line.exception = exception

    product_qty_remains_to_deliver = fields.Float(
        string='Remains to deliver',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_product_qty_remains_to_deliver',
    )

    def _compute_product_qty_remains_to_deliver(self):
        for line in self:
            line.product_qty_remains_to_deliver = (
                line.product_uom_qty - line.qty_delivered
            )

    product_qty_unavailable = fields.Float(
        string='Quantity unavailable',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True,
    )

    current_product_qty_unavailable = fields.Float(
        string='Current quantity unavailable',
        digits=dp.get_precision('Product Unit of Measure'),
        compute='_compute_current_product_qty_unavailable',
    )

    def _compute_current_product_qty_unavailable(self):
        for line in self:
            line.current_product_qty_unavailable = (
                self.get_product_qty_unavailable(
                    line.product_id,
                    line.product_uom_qty,
                    line.state == 'sale',
                    line.id
                )
            )

    @api.model
    def get_product_qty_unavailable(self, product, product_uom_qty,
                                    confirmed, line_id):
        if product and product_uom_qty:
            immediately_usable_qty = product.immediately_usable_qty
            if confirmed:
                # If sale order line confirmed, ordered quantity
                # is already computed in immediately usable quantity
                if immediately_usable_qty >= 0:
                    # Because ordered quantity is already
                    # computed in immediately usable quantity,
                    # if immediately usable quantity is positive,
                    # the unavailable quantity equals 0
                    return 0
                else:
                    # Because ordered quantity is already
                    # computed in immediately usable quantity,
                    # if immediately usable quantity is negative,
                    # the unavailable quantity
                    # equals the immediately usable quantity
                    # minus the sum of stock move quantity
                    # which stock move is after the order line stock move
                    order_line_stock_move = self.env['stock.move'].search([
                        ('procurement_id.sale_line_id', '=', line_id),
                        ('state', 'not in', ['draft', 'cancel', 'done'])
                    ], limit=1)
                    stock_move_date_expected = (
                        order_line_stock_move.date_expected
                    )

                    next_stock_moves = self.env['stock.move'].search([
                        ('procurement_id.sale_line_id', '!=', line_id),
                        ('state', 'not in', ['draft', 'cancel', 'done']),
                        '|',
                        ('priority', '<',  order_line_stock_move.priority),
                        '&',
                        ('priority', '=', order_line_stock_move.priority),
                        ('date_expected', '>', stock_move_date_expected),
                    ])
                    next_quantities = sum(
                        move.product_uom_qty for move in next_stock_moves
                    )

                    good_immediately_usable_qty = (
                        immediately_usable_qty + next_quantities
                    )

                    if good_immediately_usable_qty <= 0:
                        return min(product_uom_qty,
                                   abs(good_immediately_usable_qty))
                    else:
                        return 0
            else:
                # If sale order line is NOT confirmed, ordered quantity
                # is NOT already computed in immediately usable quantity
                if immediately_usable_qty <= 0:
                    # If immediately usable quantity is negative,
                    # the unavailable quantity equals the sum
                    # between ordered quantity
                    # and immediately usable quantity absolute value
                    return product_uom_qty
                else:
                    # If immediately usable quantity is positive,
                    # the unavailable quantity equals the ordered quantity
                    # minus the immediately usable quantity
                    # (limited with ordered quantity)
                    return max(product_uom_qty - immediately_usable_qty, 0)
        else:
            return None

    @api.onchange('product_id', 'product_uom_qty')
    def onchange_for_product_qty_unavailable(self):
        context = self.env.context or {}
        if context.get('must_compute_product_qty_unavailable'):
            for line in self:
                line.product_qty_unavailable = (
                    self.get_product_qty_unavailable(
                        self.product_id,
                        self.product_uom_qty,
                        self.state == 'sale',
                        None
                    )
                )

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        new_context = self.env.context.copy() if self.env.context else {}
        if isinstance(field_name, list):
            if 'product_uom_qty' in field_name or 'product_id' in field_name:
                new_context['must_compute_product_qty_unavailable'] = True
        else:
            if field_name in ['product_uom_qty', 'product_id']:
                new_context['must_compute_product_qty_unavailable'] = True
        return super(SaleOrderLine, self.with_context(new_context)).onchange(
            values, field_name, field_onchange
        )

    @api.model
    def create(self, vals):
        record = super(SaleOrderLine, self).create(vals)
        if vals.get('product_uom_qty'):
            # Because product_qty_unavailable is readonly,
            # we need to apply the onchange
            # on create to save the correct values.
            #
            # Without that,
            # the product_qty_unavailable isn't sent by form view,
            # and its value isn't save.
            record.with_context(
                must_compute_product_qty_unavailable=True
            ).onchange_for_product_qty_unavailable()
        return record

    @api.multi
    def write(self, vals):
        result = super(SaleOrderLine, self).write(vals)
        if vals.get('product_uom_qty'):
            # Because product_qty_unavailable is readonly,
            # we need to apply the onchange
            # on write to save the correct values.
            #
            # Without that,
            # the product_qty_unavailable isn't sent by form view,
            # and its value isn't save.
            self.with_context(
                must_compute_product_qty_unavailable=True
            ).onchange_for_product_qty_unavailable()
        return result

    production_lot_ids = fields.Many2many(
        comodel_name='stock.production.lot',
        compute='_compute_production_lot_ids',
        string='Lots/Serial Numbers',
    )

    @api.depends('product_id')
    def _compute_production_lot_ids(self):
        production_lot_model = self.env['stock.production.lot'].with_context(
            only_wh_stock_quants=True
        )
        for line in self:
            if line.product_id:
                production_lot_ids = production_lot_model.search([
                    ('product_id', '=', line.product_id.id),
                ]).filtered(
                    lambda p: p.product_qty > 0
                )
            if production_lot_ids:
                line.production_lot_ids = [(6, 0, production_lot_ids.ids)]
            else:
                line.production_lot_ids = [(5, 0)]

    next_expected_date_for_receipt = fields.Date(
        string='Next expected date for receipt',
        compute='_compute_next_expected_date_for_receipt',
    )

    @api.depends('product_id')
    def _compute_next_expected_date_for_receipt(self):
        stock_move_model = self.env['stock.move']
        for line in self:
            move = None
            if line.product_id:
                move = stock_move_model.search([
                    ('product_id', '=', line.product_id.id),
                    ('state', '=', 'assigned'),
                    ('picking_id.picking_type_id.code', '=', 'incoming'),
                ], order='date_expected', limit=1)
            if move:
                line.next_expected_date_for_receipt = move.date_expected
            else:
                line.next_expected_date_for_receipt = False


# Override the inherit of sale_product_additional
# to complete sale.order.line.original with new specific fields
class SaleOrderLineOriginal(models.Model):
    _name = 'sale.order.line.original'
    _inherit = 'sale.order.line'


# Override the inherit of sale_product_additional
# to complete sale.order.line.additional with new specific fields
class SaleOrderLineAdditional(models.Model):
    _name = 'sale.order.line.additional'
    _inherit = 'sale.order.line'
