# -*- coding: utf-8 -*-
# 2018 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from datetime import datetime

from odoo import _, api, fields, models

MANAGE_DAY_PREFIX = 'is_manage_day_'

_logger = logging.getLogger(__name__)


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    _sql_constrains = [
        (
            'unique_procurement_order_by_product',
            'UNIQUE(product_id)',
            _('The procurement order must be unique by product'),
        )
    ]

    def _get_orderpoint_domain(self, company_id=False):
        """
        Append days selected in the domain.
        Days are sent by the context
        :param company_id:
        :return:
        """
        result = super(ProcurementOrder, self)._get_orderpoint_domain(
            company_id=company_id
        )

        domain = []
        if self._context.get('type') == 'by_suppliers':
            domain = [
                (
                    'product_id.supplier_id.id',
                    'in',
                    self._context['supplier_ids'],
                )
            ]
        elif self._context.get('type') == 'by_days':
            days_selected = []
            for key in self._context.keys():
                if key.startswith(MANAGE_DAY_PREFIX):
                    days_selected.append(key)

            # If there are selected days we build a new domain
            if days_selected:
                day = days_selected.pop()
                domain = [('product_id.supplier_id.%s' % day, '=', True)]
                while days_selected:
                    day = days_selected.pop()
                    # Insert the OR operator
                    domain.insert(0, "|")
                    domain.append(
                        ('product_id.supplier_id.%s' % day, '=', True)
                    )
        else:
            isoweekday = datetime.now().isoweekday()
            field_name = MANAGE_DAY_PREFIX + str(isoweekday)
            domain = [('product_id.supplier_id.%s' % field_name, '=', True)]

            # Add suppliers with open purchase order in the
            open_purchase_orders = self.env['purchase.order'].search(
                [('state', '=', 'draft')]
            )
            partners = open_purchase_orders.mapped('partner_id')
            if partners:
                domain.insert(0, '|')
                domain.append(
                    ('product_id.supplier_id.id', 'in', partners.ids)
                )

        return result + domain

    @api.model
    def _procure_orderpoint_confirm(
        self, use_new_cursor=False, company_id=False
    ):
        """ Run the procurement and recompute promotions if not disabled """

        # if we are running from the resupply wizard, first make sure all
        # products with a negative stock have a procurement order
        warehouses = self.env['stock.warehouse'].search(
            [('company_id', '=', company_id or 1)]
        )
        for wh in warehouses:
            self._ensure_product_orderpoints(wh)
        _logger.info('Run the procurement')
        result = super(ProcurementOrder, self)._procure_orderpoint_confirm(
            use_new_cursor=use_new_cursor, company_id=company_id
        )
        _logger.info('Procurement finished')

        return result

    @api.model
    def _ensure_product_orderpoints(self, warehouse, products=None):
        Product = self.env['product.product'].with_context(
            warehouse=warehouse.id
        )
        domain = [('orderpoint_ids', '=', False), ('type', '=', 'product')]
        if products:
            domain.append(('id', 'in', products.ids))
        for product in Product.search(domain):
            if product.virtual_available < 0:
                self.env['stock.warehouse.orderpoint'].create(
                    {
                        'warehouse_id': warehouse.id,
                        'product_id': product.id,
                        'company_id': warehouse.company_id.id,
                        'product_min_qty': 0,
                        'product_max_qty': 0,
                        'location_id': warehouse.view_location_id.id,
                        'product_uom': product.uom_id.id,
                    }
                )

    def make_po(self):
        """
        Update the order date when the procurement update or create a purchase
        order. The new order date must be the datetime of now.
        """
        result = super(ProcurementOrder, self).make_po()

        procurements = self.browse(result)

        pos = procurements.mapped('purchase_id')
        pos.write({'date_order': fields.Datetime.now()})
        with self.env.norecompute():
            # The recompute_discount_values makes direct assignments on line
            # each assignment launch a recompute on the line and on the PO
            # delay the recompute at the end of the discount recompute
            # code to be removed into odoo 13
            pos.mapped('order_line').recompute_discount_values()
        self.recompute()

        return result

    def _get_pol_promotion_supplier(self, po, supplier):
        seller = self.product_id._select_seller(
            partner_id=supplier.name,  # name is a res.partner on supplier.info
            quantity=self.product_qty,
            date=po.date_order and po.date_order[:10],
            uom_id=self.product_id.uom_po_id,
        )
        return seller.discount_purchase or 0.0

    def _prepare_purchase_order_line(self, po, supplier):
        values = super(ProcurementOrder, self)._prepare_purchase_order_line(
            po, supplier
        )
        price_unit_base = values['price_unit']
        discount_global = po.partner_id.supplier_discount
        promotion_supplier = self._get_pol_promotion_supplier(po, supplier)
        price_unit = self.env['purchase.order.line']._compute_discount(
            values['price_unit'], discount_global, promotion_supplier
        )
        values.update(
            {
                'price_unit_base': price_unit_base,
                'price_unit': price_unit,
                'discount_global': discount_global,
                'promotion_supplier': promotion_supplier,
            }
        )
        return values
