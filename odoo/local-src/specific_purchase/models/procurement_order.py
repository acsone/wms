# -*- coding: utf-8 -*-
# 2018 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from datetime import datetime

from odoo import api, models, _

MANAGE_DAY_PREFIX = 'is_manage_day_'

_logger = logging.getLogger(__name__)


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    _sql_constrains = [('unique_procurement_order_by_product',
                        'UNIQUE(product_id)',
                        _('The procurement order must be unique by product'))]

    def _get_orderpoint_domain(self, company_id=False):
        """
        Append days selected in the domain.
        Days are sent by the context
        :param company_id:
        :return:
        """
        result = super(ProcurementOrder, self).\
            _get_orderpoint_domain(company_id=company_id)

        domain = []
        if self._context.get('type') == 'by_suppliers':
            domain = [('product_id.supplier_id.id',
                       'in',
                       self._context['supplier_ids'])]
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
                        ('product_id.supplier_id.%s' % day, '=', True))
        else:
            isoweekday = datetime.now().isoweekday()
            field_name = MANAGE_DAY_PREFIX + str(isoweekday)
            domain = \
                [('product_id.supplier_id.%s' % field_name, '=', True)]

            # Add suppliers with open purchase order in the
            open_purchase_orders = \
                self.env['purchase.order'].search([('state', '=', 'draft')])
            partners = open_purchase_orders.mapped('partner_id')
            if partners:
                domain.insert(0, '|')
                domain.append(
                    ('product_id.supplier_id.id', 'in', partners.ids))

        return result + domain

    @api.model
    def _procure_orderpoint_confirm(
            self, use_new_cursor=False, company_id=False):
        """ Run the procurement and recompute promotions if not disabled """

        _logger.info('Run the procurement')
        result = super(ProcurementOrder, self)._procure_orderpoint_confirm(
            use_new_cursor=use_new_cursor, company_id=company_id)
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

            _logger.info('Update values for open puchase orders')
            self.env['purchase.order'].update_values_for_open_po()
            _logger.info('Update done')

        return result
