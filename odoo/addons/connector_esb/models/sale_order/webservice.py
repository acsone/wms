# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, exceptions
from odoo.addons.component.core import Component


class SaleOrderStatusWebserviceMessage(Component):

    _name = 'esb.webservice.message.sale.order.status'
    _inherit = ['esb.webservice.message.base']
    _apply_on = ['sale.order']
    _usage = 'ws.message.sale.order.status'

    def get_message(self, partner_ref, esb_ref):
        """ Return the status of a sale order """
        SaleOrder = self.env['sale.order']
        partner = SaleOrder._ws_get_partner(partner_ref)

        so = SaleOrder.search(
            [('partner_id', '=', partner.id), ('esb_ref', '=', esb_ref)]
        )

        if not so:
            raise exceptions.UserError(_('Sale Order not found'))
        if len(so) > 1:
            raise exceptions.UserError(
                _('There are several sale orders with the same increment ID')
            )

        lines_values = []
        for line in so.order_line:
            if not line.exception:
                available = line.product_uom_qty - line.product_qty_unavailable
                available = max(0, available)
            else:
                available = 0

            lines_values.append(
                {
                    'line_id': line.sequence,
                    'cnk': line.product_id.cnk_code,
                    'quantity': line.product_uom_qty,
                    'available': available,
                    'price_total': line.price_subtotal,
                    'error': line.exception or None,
                }
            )

        values = {
            'state': so.state,
            'confirmation_date': so.confirmation_date,
            'price_subtotal': so.amount_untaxed,
            'price_tax': so.amount_tax,
            'price_total': so.amount_total,
            'note': so.note or None,
            'lines': lines_values,
        }

        return values
