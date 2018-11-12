# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.addons.decimal_precision as dp

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Sale(models.Model):
    _inherit = 'sale.order'

    sale_channel = fields.Selection([
        ('phone', 'Phone'),
        ('mail', 'Mail'),
        ('fax', 'Fax'),
        ('web', 'Web'),
    ])
    suite_name = fields.Char(
        string='Suite Id',
        copy=False,
    )

    @api.onchange('team_id')
    def onchange_team_id(self):
        if not self.sale_channel:
            self.sale_channel = 'phone'

        team_web = self.env.ref('sales_team.salesteam_website_sales')
        if self.team_id == team_web:
            self.sale_channel = 'web'

    @api.multi
    def order_lines_layouted(self):
        """Improve the sale order line on the report.

        If some products in the lines belongs to a product category that has a
        warning message configured. Those lines are grouped together and a
        line with the message is added before them.

        A specific product category 'Human medicine' has besides the warning
        message, for each of its product a line added to inform  about the
        product transfert to a pharmacist.
        """
        self.ensure_one()
        report_pages = super(Sale, self).order_lines_layouted()
        # Get the product categories in the sale order that contains a warning
        categories = self.order_line.mapped(
                'product_id.categ_id').filtered('warning_info')
        # Group the lines by categories (with warning)
        warn_lines = {}
        for category in categories:
            warn_lines[category] = self.order_line.filtered(
                    lambda r: r.product_id.categ_id.id == category.id
                ).sorted()
        # Get all the line ids whose product belongs to a category with warning
        warn_line_ids = sum([l.ids for c, l in warn_lines.iteritems()], [])
        # Categories with specific display
        pharmacy_cat = self.env.ref('specific_data.product_categ_humain')

        new_report_pages = []
        for report_page_category in report_pages:
            new_values = []
            for report_page in report_page_category:
                # Filter out the lines whose categories have a warning message
                new_lines = [
                    line for line in report_page['lines']
                    if line.id not in warn_line_ids
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

        # Add the lines with a warning message and the warning with it
        for category, lines in warn_lines.iteritems():
            new_page = {
                'name_list': [category.warning_info],
                'subtotal': False,
                'pagebreak': False,
                'lines': lines,
            }
            if category == pharmacy_cat:
                new_page['only_quantity'] = True
                pharmacist_name = (self.partner_id.pharmacist_id.name or '')
                new_page['line_additional_text'] = (
                        _(u'Article transferred to dispensing pharmacy: %s') %
                        pharmacist_name)
            new_report_pages[-1].append(new_page)

        return new_report_pages

    @api.multi
    def action_confirm(self):
        self.ensure_one()

        # Disable tracking
        result = super(Sale, self.with_context(tracking_disable=True))\
            .action_confirm()

        # Post the message "Quotation confirmed"
        message = self.env.ref('sale.mt_order_confirmed')
        self.message_post(body=message.description)

        return result

    @api.constrains('ignore_exception', 'order_line', 'state')
    def sale_check_exception(self):
        try:
            self._check_exception()
        except ValidationError:
            # If a sale exception is found it will be displayed on the UI
            pass


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    supplier_break = fields.Boolean(compute='_compute_supplier_break')
    exception = fields.Char(compute='_compute_exception')
    warning_text = fields.Char(compute='_compute_exception')
    date_order = fields.Datetime(related="order_id.date_order")
    older_lot_life_date = fields.Datetime(
        string='Expiration date',
        related='product_id.older_lot_id.life_date',
        readonly=True
    )

    @api.depends('product_id')
    def _compute_supplier_break(self):
        """Product out of stock at the supplier level"""
        supplier_nostock = self.env.ref('specific_purchase.product_state_h')
        for line in self:
            line.supplier_break = line.product_id.state_id == supplier_nostock

    @api.depends('product_id', 'price_subtotal', 'order_id.partner_id')
    def _compute_exception(self):
        """ Compute sale exceptions and warnings on a line.

            The first exception raised is kept to be displayed on the line.
            Warning text are added to the description of the line.
        """
        line_exceptions = self.env['exception.rule'].search([
            ('rule_group', '=', 'sale'),
            ('model', '=', 'sale.order.line'),
            ],
            order='sequence'
        )
        for line in self:
            exception = warning = ''
            if line.product_id:
                for rule in line_exceptions:
                    if not self.env['sale.order']._rule_eval(rule,
                                                             'line', line):
                        continue
                    if rule.warning_only:
                        if rule.warning_text:
                            warning += '\n' + rule.warning_text
                    if not exception:
                        exception = rule.description
                        # line.order_id.main_exception_id = rule
            line.exception = exception
            if line.warning_text != warning:
                line.warning_text = warning
                line.set_line_name()

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
                    if not order_line_stock_move:
                        return min(
                            abs(immediately_usable_qty),
                            product_uom_qty,
                        )
                    stock_move_date_expected = (
                        order_line_stock_move.date_expected
                    )

                    next_stock_moves = self.env['stock.move'].search([
                        ('product_id', '=', product.id),
                        ('procurement_id.sale_line_id', '!=', line_id),
                        ('state', 'not in', ['draft', 'cancel', 'done']),
                        '|',
                        '|',
                        ('priority', '<', order_line_stock_move.priority),
                        '&',
                        ('priority', '=', order_line_stock_move.priority),
                        ('date_expected', '>', stock_move_date_expected),
                        # in rare case of same date_expected,
                        # use id to sort the moves
                        '&', '&',
                        ('priority', '=', order_line_stock_move.priority),
                        ('date_expected', '=', stock_move_date_expected),
                        ('id', '>', order_line_stock_move.id),
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
    def set_line_name(self):
        """ Set the name description on the line.

        As there is a column with product code on the SO/invoice, do not put
        internal code prefix on the line description. This rule applies for
        SO and Invoice at product onchange as invoice line description is
        copied from SO line description.
        """
        self.ensure_one()
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )
        name = product.name
        if product.description_sale:
            name += '\n' + product.description_sale
        if self.supplier_break:
            name = name + '\r' + _('Out of stock at supplier level')
        self.name = (name or '') + (self.warning_text or '')

    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        stup_category = self.env.ref('specific_data.product_categ_stupefiant')
        if (self.product_id
                and self.product_id.categ_id.has_for_parent(stup_category.id)):
            warning_mess = {
                'title': _('Narcotic voucher'),
                'message': _('A narcotic voucher is '
                             'required for the data entry.')
            }
            result = {
                'warning': warning_mess
            }
        return result

    @api.onchange('product_id')
    def product_id_onchange(self):
        """2nd on change method for product_id.

        The previous onchange method calls super which raises problems
        with the compute methods being called before defaults fields are
        set by Odooo
        """
        self.set_line_name()

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
        # don't trigger product_qty_unavalable computation
        # if the value is provided.
        if (vals.get('product_uom_qty')
                and 'product_qty_unavailable' not in vals):
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
        # don't trigger product_qty_unavalable computation
        # if the value is provided.
        if (vals.get('product_uom_qty')
                and 'product_qty_unavailable' not in vals):
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
            production_lot_ids = None
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

    # Vallidation rules for sale order lines, used by the sale_exception module
    # It works by restrictions, so any client alcyon categories not referenced
    # in here would have all the rights !
    #
    @api.multi
    def validate_no_food(self):
        """Disallow all products from food categories."""
        target_groups = ['specific_partner.partner_category_only_material',
                         ]
        food = self.env.ref('specific_data.product_categ_ali')
        if not self.product_id.categ_id.has_for_parent(food.id):
            return False
        for group_xmlid in target_groups:
            group = self.env.ref(group_xmlid)
            if self.order_id.partner_id.alcyon_category_id == group:
                return True
        return False

    @api.multi
    def validate_no_medoc(self):
        """Disallow all products from medicines categories."""
        target_groups = ['specific_partner.partner_category_only_material',
                         ]
        medoc = self.env.ref('specific_data.product_categ_medoc')
        if not self.product_id.categ_id.has_for_parent(medoc.id):
            return False
        if not self.order_id.partner_id.alcyon_category_id:
            # Customer with undefined category are not allowed medoc
            return True
        for group_xmlid in target_groups:
            group = self.env.ref(group_xmlid)
            if self.order_id.partner_id.alcyon_category_id == group:
                return True
        return False

    # Disallow only some sub category of medicines
    @api.multi
    def validate_no_medoc_cascade_import(self):
        """Disallow all products from medicines cascade importation."""
        target_groups = ['specific_partner.partner_category_customerexport',
                         'specific_partner.partner_category_student',
                         'specific_partner.partner_category_med_export',
                         ]
        base_category = self.env.ref('specific_data.product_categ_importation')
        if not self.product_id.categ_id.has_for_parent(base_category.id):
            return False
        for group_xmlid in target_groups:
            group = self.env.ref(group_xmlid)
            if self.order_id.partner_id.alcyon_category_id == group:
                return True
        return False

    @api.multi
    def validate_no_medoc_veterinary_belge(self):
        """Disallow all products from medicines veterinary belge."""
        target_groups = ['specific_partner.partner_category_customerexport',
                         'specific_partner.partner_category_student',
                         ]
        base_category = self.env.ref('specific_data.product_categ_vet_belges')
        if not self.product_id.categ_id.has_for_parent(base_category.id):
            return False
        for group_xmlid in target_groups:
            group = self.env.ref(group_xmlid)
            if self.order_id.partner_id.alcyon_category_id == group:
                return True
        return False

    @api.multi
    def validate_no_medoc_human(self):
        """Disallow all products from medicines human."""
        target_groups = ['specific_partner.partner_category_customerexport',
                         'specific_partner.partner_category_callcenter',
                         'specific_partner.partner_category_pharmacy',
                         'specific_partner.partner_category_student',
                         'specific_partner.partner_category_med_export',
                         ]
        base_category = self.env.ref('specific_data.product_categ_humain')
        if not self.product_id.categ_id.has_for_parent(base_category.id):
            return False
        for group_xmlid in target_groups:
            group = self.env.ref(group_xmlid)
            if self.order_id.partner_id.alcyon_category_id == group:
                return True
        return False

    # Dissallow sub sub category of medicines
    @api.multi
    def validate_no_medoc_vet_stupefiant(self):
        """Disallow all products from medicines stupefiants."""
        target_groups = ['specific_partner.partner_category_veterinary',
                         'specific_partner.partner_category_alcyonaire',
                         'specific_partner.partner_category_med_export',
                         ]
        base_category = self.env.ref('specific_data.product_categ_stupefiant')
        if not self.product_id.categ_id.has_for_parent(base_category.id):
            return False
        for group_xmlid in target_groups:
            group = self.env.ref(group_xmlid)
            if self.order_id.partner_id.alcyon_category_id == group:
                return True
        return False

    @api.multi
    def validate_no_medoc_vet_psychoIII(self):
        """Disallow all products from medicines psycho III."""
        target_groups = ['specific_partner.partner_category_med_export',
                         ]
        base_category = self.env.ref(
            'specific_data.product_categ_psychotropes_25')
        if not self.product_id.categ_id.has_for_parent(base_category.id):
            return False
        for group_xmlid in target_groups:
            group = self.env.ref(group_xmlid)
            if self.order_id.partner_id.alcyon_category_id == group:
                return True
        return False

    @api.multi
    def validate_no_medoc_belgium_only(self):
        """Disallow products which are for Belgium only"""
        target_groups = ['specific_partner.partner_category_customerexport',
                         'specific_partner.partner_category_med_export',
                         ]
        if not self.product_id.belgium_only:
            return False
        for group_xmlid in target_groups:
            group = self.env.ref(group_xmlid)
            if self.order_id.partner_id.alcyon_category_id == group:
                return True
        return False

    def validate_no_veterinary_product(self):
        """Disallow products which are only for veterinary"""
        target_groups = ['specific_partner.partner_category_customerexport',
                         'specific_partner.partner_category_pharmacy',
                         ]
        if not self.product_id.veterinary_only:
            return False
        if not self.order_id.partner_id.alcyon_category_id:
            # Customer with undefined category are not allowed vet only
            return True
        for group_xmlid in target_groups:
            group = self.env.ref(group_xmlid)
            if self.order_id.partner_id.alcyon_category_id == group:
                return True
        return False

    def validate_no_psychotropic_ordered_by_phone(self):
        """No psychotropic ordered on the phone."""
        psycho_cat = self.env.ref('specific_data.product_categ_stupefiant')
        if not self.product_id.categ_id.has_for_parent(psycho_cat.id):
            return False
        return self.order_id.sale_channel == 'phone'

    # Warnings
    def warning_psychotropic(self):
        """Add warning for psychotropic product on sale order line."""
        psycho_cat = self.env.ref('specific_data.product_categ_stupefiant')
        return self.product_id.categ_id.has_for_parent(psycho_cat.id)

    def validate_no_backorder(self):
        """Block backorder for customer that specifically do not want them."""
        if not self.product_qty_unavailable:
            return False
        return not self.order_id.partner_id.is_sale_back_order_accepted

    def warning_free_product(self):
        """Raise a warning if order give rights to promotional product."""
        return self.product_id.product_tmpl_id.get_promotional_product(
            self.product_uom_qty,
            self.product_id.uom_id,
        )

    def warning_provision_on_order(self):
        """Add a warning if the product is provisioned at ordering time."""
        routes = self.product_id.route_ids
        return self.env.ref('stock.route_warehouse0_mto').id in routes.ids

    def warning_cascade_importation(self):
        """Add a warning for cascade importation product."""
        cascade_cat = self.env.ref('specific_data.product_categ_importation')
        return self.product_id.categ_id.has_for_parent(cascade_cat.id)

    def warning_human_medicine(self):
        """Add a warning for human medicine product."""
        human_medoc_cat = self.env.ref('specific_data.product_categ_humain')
        return self.product_id.categ_id.has_for_parent(human_medoc_cat.id)
