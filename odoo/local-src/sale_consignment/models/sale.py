# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_consignment = fields.Boolean(
        'For Consignment',
        help="Procurement will be generated for the consignement location "
             "of the selected customer")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(
            group_id=group_id)
        if self.order_id.is_consignment:
            location = self.order_id.partner_shipping_id.\
                property_stock_consignment_customer
            if not location:
                location = self.env['stock.location'].sudo().create({
                    'location_id': self.env.ref(
                        'sale_consignment.stock_location_consignment').id,
                    'name': self.order_id.partner_shipping_id.display_name,
                    'usage': 'internal',
                    'company_id': self.order_id.company_id.id,
                    })
                self.order_id.partner_shipping_id.sudo().\
                    property_stock_consignment_customer = location.id
            vals['location_id'] = location.id
        return vals
