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
        route_mto = self.env.ref('stock.route_warehouse0_mto')
        for wh in warehouses:
            Product = self.env['product.product'].with_context(warehouse=wh.id)
            for product in Product.search(
                [
                    ('orderpoint_ids', '=', False),
                    ('type', '=', 'product'),
                    ('virtual_available', '<', 0),
                    ('route_ids', 'not in', [route_mto.id]),
                ]
            ):
                self.env['stock.warehouse.orderpoint'].create(
                    {
                        'warehouse_id': wh.id,
                        'product_id': product.id,
                        'company_id': wh.company_id.id,
                        'product_min_qty': 0,
                        'product_max_qty': 0,
                        'location_id': wh.view_location_id.id,
                        'product_uom': product.uom_id.id,
                    }
                )

        _logger.info('Run the procurement')
        result = super(ProcurementOrder, self)._procure_orderpoint_confirm(
            use_new_cursor=use_new_cursor, company_id=company_id
        )
        _logger.info('Procurement finished')

        # By default we recompute promotions
        if self._context.get('is_not_recompute_promos'):
            return result

        # Procurement is running in a new cursor. If we want to access
        # to purchase orders created by the procurement we need to
        # open a new cursor
        with api.Environment.manage():
            context = self._context.copy()
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr, context=context))

            try:
                # Delay jobs to update values on open purchase orders
                self.env['purchase.order'].delay_update_for_open_po()
                new_cr.commit()
            except Exception as e:
                _logger.error(e)
                new_cr.rollback()
            finally:
                new_cr.close()

        return result

    def make_po(self):
        """
        Update the order date when the procurement update or create a purchase
        order. The new order date must be the datetime of now.
        """
        result = super(ProcurementOrder, self).make_po()

        procurements = self.browse(result)

        pos = procurements.mapped('purchase_id')
        pos.write({'date_order': fields.Datetime.now()})

        return result
