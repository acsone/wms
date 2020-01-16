# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

import odoo.addons.decimal_precision as dp
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class Sale(models.Model):
    _inherit = 'sale.order'

    sale_channel = fields.Selection(
        [('phone', 'Phone'), ('mail', 'Mail'), ('fax', 'Fax'), ('web', 'Web')]
    )
    suite_name = fields.Char(string='Suite Id', copy=False)

    @api.model_cr
    def init(self):
        res = super(Sale, self).init()
        # This partial index is used by the 'last_suite_name' computed field
        # on 'res.partner' (use of 'LIMIT 1' making PostgreSQL slow under
        # certain circumstances).
        query = """
            CREATE INDEX IF NOT EXISTS
            sale_order_partner_id_date_order_id_partial_index
            ON sale_order (partner_id, date_order DESC, id DESC)
            WHERE suite_name IS NOT NULL;
        """
        self.env.cr.execute(query)
        return res

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
        categories = self.order_line.mapped('product_id.categ_id').filtered(
            'warning_info'
        )
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
                    line
                    for line in report_page['lines']
                    if line.id not in warn_line_ids
                ]
                if new_lines:
                    new_values.append(
                        {
                            'name': report_page['name'],
                            'subtotal': report_page['subtotal'],
                            'pagebreak': report_page['pagebreak'],
                            'lines': new_lines,
                        }
                    )
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
                pharmacist_name = self.partner_id.pharmacist_id.name or ''
                new_page['line_additional_text'] = (
                    _(u'Article transferred to dispensing pharmacy: %s')
                    % pharmacist_name
                )
            new_report_pages[-1].append(new_page)

        return new_report_pages

    @api.multi
    def action_confirm(self):
        self.ensure_one()

        # Disable tracking
        result = super(
            Sale, self.with_context(tracking_disable=True)
        ).action_confirm()

        # Post the message "Quotation confirmed"
        message = self.env.ref('sale.mt_order_confirmed')
        self.message_post(body=message.description)
        return result

    def sale_check_exception(self):
        try:
            self._check_exception()
        except ValidationError:
            # If a sale exception is found it will be displayed on the UI
            pass

    @api.multi
    def action_cancel(self):
        for sale_order in self:
            if sale_order.picking_ids.filtered(
                lambda picking: picking.printed
            ):
                raise UserError(
                    _(
                        u"You cannot cancel sale order %s, it's already "
                        u"prepared"
                    )
                    % sale_order.name
                )
        return super(Sale, self).action_cancel()

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        """
        This override is required to optimize the performance when the onchange
        method is called for an order_line.
        When the onchange method is called for an order_line, the field_onchange
        parameter contains all the fields declared for the sale.order.line tree
        AND form defined into the sale.order form. Since this list is used by
        Odoo to detect the impact of an onchange on the displayed attributes,
        all fields present into this list are evaluated into the base
        implementation. Unfortunately, even if some costly fields are only
        declared into the form definition of the sale.order.line, these fields
        are also present into the field_onchange parameter. (because
        the form definition is embedded into the xml element field)
        To avoid to compute these useless fields only displayed into the
        sale.order.line form, we remove these fields from the field_onchange
        parameter before calling super
        """
        for f in [
            "order_line.production_lot_ids",
            "order_line.next_expected_date_for_receipt",
        ]:
            field_onchange.pop(f, None)
        return super(Sale, self).onchange(values, field_name, field_onchange)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    exception = fields.Char(compute='_compute_exception')
    warning_text = fields.Char(compute='_compute_exception')
    date_order = fields.Datetime(related="order_id.date_order")
    older_lot_life_date = fields.Datetime(
        string='Expiration date',
        related='product_id.older_lot_id.life_date',
        readonly=True,
    )
    order_partner_id = fields.Many2one(readonly=True)
    order_pricelist_id = fields.Many2one(
        related='order_id.pricelist_id', readonly=True
    )
    picking_zone_id = fields.Many2one(
        related="product_id.picking_zone_id", readonly=True
    )

    @api.depends('product_id', 'price_subtotal', 'order_id.partner_id')
    def _compute_exception(self):
        """ Compute sale exceptions and warnings on a line.

            The first exception raised is kept to be displayed on the line.
            Warning text are added to the description of the line.
        """
        line_exceptions = self.env['exception.rule'].search(
            [('model', '=', 'sale.order.line')], order='sequence'
        )
        for line in self:
            exception = warning = ''
            if line.product_id:
                for rule in line_exceptions:
                    if not self.env['sale.order']._rule_eval(rule, line):
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
            uom=self.product_uom.id,
        )
        name = product.name
        if product.description_sale:
            name += '\n' + product.description_sale
        self.name = (name or '') + (self.warning_text or '')

    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        stup_category = self.env.ref('specific_data.product_categ_stupefiant')
        if self.product_id and self.product_id.categ_id.has_for_parent(
            stup_category.id
        ):
            warning_mess = {
                'title': _('Narcotic voucher'),
                'message': _(
                    'A narcotic voucher is ' 'required for the data entry.'
                ),
            }
            result = {'warning': warning_mess}
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
        """
        NOTE BY LMIGNON: My little attempt to understand the motivation behind
        this override.
        The implementation into the onchange method computing a value for
        product_qty_unavailable is conditioned to the presence of the
        'must_compute_product_qty_unavailable' attribute into the context.
        See procurement_sale.models.sale.onchange_for_product_qty_unavailable
        By default the logic into onchange_for_product_qty_unavailable is
        disabled if this attribute is not present.
        Since the override of the onchange method is done into the
        sale.order.line, the logic in onchange_for_product_qty_unavailable is
        never executed if the call to onchange is done by editing a line into
        the order_line tree into the sale order form. The logic is only
        executed when the same line is edited into the Fast Line entry tree
        since the onchange is called directly on the sale.order.line model.

        TO BE REMOVED / REFACTORED / EXPLAINED
        """
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
        if (
            vals.get('product_uom_qty')
            and 'product_qty_unavailable' not in vals
        ):
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
        if (
            vals.get('product_uom_qty')
            and 'product_qty_unavailable' not in vals
        ):
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
        production_lots = (
            self.env['stock.production.lot']
            .search([('product_id', 'in', self.mapped("product_id").ids)])
            .filtered(lambda p: p.qty_available > 0)
        )
        lot_ids_by_product_id = defaultdict(list)
        for lot in production_lots:
            lot_ids_by_product_id[lot.product_id.id].append(lot.id)
        for line in self:
            production_lot_ids = lot_ids_by_product_id.get(line.product_id.id)
            if production_lot_ids:
                line.production_lot_ids = [(6, 0, production_lot_ids)]
            else:
                line.production_lot_ids = [(5, 0)]

    # Vallidation rules for sale order lines, used by the sale_exception module
    # It works by restrictions, so any client alcyon categories not referenced
    # in here would have all the rights !
    #
    @api.multi
    def validate_no_food(self):
        """Disallow all products from food categories."""
        target_groups = ['specific_partner.partner_category_only_material']
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
        target_groups = ['specific_partner.partner_category_only_material']
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
        target_groups = [
            'specific_partner.partner_category_customerexport',
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
        target_groups = [
            'specific_partner.partner_category_customerexport',
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
        target_groups = [
            'specific_partner.partner_category_customerexport',
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
        target_groups = [
            'specific_partner.partner_category_veterinary',
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
        target_groups = ['specific_partner.partner_category_med_export']
        base_category = self.env.ref(
            'specific_data.product_categ_psychotropes_25'
        )
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
        target_groups = [
            'specific_partner.partner_category_customerexport',
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
        target_groups = [
            'specific_partner.partner_category_customerexport',
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
        psych_cat = self.env.ref('specific_data.product_categ_psychotropes_25')
        if not self.product_id.categ_id.has_for_parent(psych_cat.id):
            return False
        return self.order_id.sale_channel == 'phone'

    def validate_no_stupefiant_vet_by_phone(self):
        """No psychotropic ordered on the phone."""
        vet_cat = self.env.ref('specific_data.product_categ_stupefiant_vet')
        if not self.product_id.categ_id.has_for_parent(vet_cat.id):
            return False
        return self.order_id.sale_channel == 'phone'

    # Warnings
    def warning_psychotropic(self):
        """Add warning for psychotropic product on sale order line."""
        psych_cat = self.env.ref('specific_data.product_categ_psychotropes_25')
        return self.product_id.categ_id.has_for_parent(psych_cat.id)

    def warning_stupefiant_vet(self):
        """Add warning for psychotropic product on sale order line."""
        vet_cat = self.env.ref('specific_data.product_categ_stupefiant_vet')
        return self.product_id.categ_id.has_for_parent(vet_cat.id)

    def validate_no_backorder(self):
        """Block backorder for customer that specifically do not want them."""
        if not self.product_qty_unavailable:
            return False
        if self.product_uom_qty == 0:
            return False
        return not self.order_id.partner_id.is_sale_back_order_accepted

    def warning_free_product(self):
        """Raise a warning if order give rights to promotional product."""
        return self.product_id.product_tmpl_id.get_promotional_product(
            self.product_uom_qty, self.product_id.uom_id
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

    def warning_supplier_break(self):
        """Add a warning for out of stock product at the supplier."""
        supplier_nostock = self.env.ref('specific_purchase.product_state_h')
        if self.product_id.state_id != supplier_nostock:
            return False
        product = self.product_id.with_context(
            prio=self.route_id.priority or '1', date=self.order_id.date_order
        )
        if product.immediately_usable_qty >= self.product_uom_qty:
            # Although it is out of stock at the supplier, there is still
            # enough stock in Alcyon warehouse
            return False
        if self.product_uom_qty == 0:
            return False
        return True

    @api.multi
    def _prepare_promotional_line(self, qty):
        """Glue for promotional products and qty_unavailable

        Recompute qty_unavailable for new promotional line.
        Promotional available quantity is computed after
        availability of main line.

        Thus there can be BO for promotional line even if
        there is no BO for ordered line.
        """
        res = super(SaleOrderLine, self)._prepare_promotional_line(qty)
        qty_unavailable = self.get_product_qty_unavailable(
            self.product_id,
            self.product_uom_qty + qty,
            self.state == 'sale',
            None,
        )
        res['product_qty_unavailable'] = min(qty_unavailable, qty)
        return res

    @api.multi
    def _action_procurement_create(self):
        """Overloaded to ship only available qty in stock to the customer:

            - update the canceled qty with the unavailable qty
            - substract the shipped qty with the canceled qty
            - set the unavailable qty to 0

        Then the resulting stock move should not generates a backorder once
        validated.

        The product qty is overridden by super so we need to backup and restore
        the proper quantity once the procurement is created.
        """
        if self.env.context.get('auto_cancel_unavailable_qty'):
            return
        backup_qty = {}
        for line in self:
            # Process only lines related to customers with the auto-cancel
            # option and related to stock products

            if (
                line.order_partner_id.auto_cancel_unavailable_qty_sold
                and line.product_id.type != "service"
                and line.product_qty_unavailable
            ):
                backup_qty[line.id] = line.product_uom_qty
                line.product_qty_canceled = line.product_qty_unavailable
                # NOTE: pass product_qty_unavailable to not recompute it
                # (see the write method overload)
                line.write(
                    {
                        'product_uom_qty': line.product_uom_qty
                        - line.product_qty_canceled,
                        'product_qty_unavailable': line.product_qty_unavailable,
                    }
                )
        res = super(SaleOrderLine, self)._action_procurement_create()
        # dont enter again in _action_procurement_create
        # while restoring ordered qty.
        for line in self.with_context(auto_cancel_unavailable_qty=True):
            if line.id in backup_qty:
                line.write(
                    {
                        'product_uom_qty': backup_qty[line.id],
                        'product_qty_unavailable': line.product_qty_unavailable,
                    }
                )
        self._check_procurements_for_MTO_products()
        return res

    def _check_procurements_for_MTO_products(self):
        # ALCYN-2150: when a product with the MTO route is sold, we want to
        # check for reordering rules and generate a purchase immediately if
        # some stock is missing. The MTO route is an empty shell and is used
        # simply as a flag on the products, because it is important that the
        # resupply for the products are not chained to the deliveries -> use
        # orderpoint to trigger a MTS resupply actually.
        if not self:
            return
        Procurement = self.env['procurement.order']
        route_mto = self.env.ref('stock.route_warehouse0_mto')
        lines = self.filtered(lambda r: r.state == 'sale')
        products = lines.mapped('product_id').filtered(
            lambda rec: route_mto in rec.route_ids
        )
        if not products:
            # short cut, and especially don't call ensure_product_orderpoints
            # with an empty recordset, as this will ensure orderpoints for
            # *all* products
            return
        warehouse = lines.mapped('order_id.warehouse_id')
        Procurement._ensure_product_orderpoints(warehouse, products)
        orderpoints = self.env['stock.warehouse.orderpoint'].search(
            [
                ('product_id', 'in', products.ids),
                ('warehouse_id', '=', warehouse.id),
                ('location_id', 'child_of', warehouse.view_location_id.id),
            ]
        )
        if orderpoints:
            Procurement.with_context(
                orderpoint_ids=orderpoints.ids
            )._procure_orderpoint_confirm(
                company_id=self.mapped('order_id.company_id').id
            )
