# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from psycopg2 import IntegrityError
from odoo import _, api, exceptions, fields, models
from odoo.addons.queue_job.job import job

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'esb.exportable']

    esb_ref = fields.Char(string='Reference for ESB', copy=False)

    _sql_constraints = [
        ('esb_ref_unique', 'unique(esb_ref)',
         _('This reference esb already exists'))
    ]

    @api.multi
    def esb_is_exportable(self):
        exportable = (
            super(SaleOrder, self).esb_is_exportable()
            and self.state not in ('draft', 'sent', 'confirm_background')
        )
        return exportable

    @api.model
    def create(self, vals):
        self_ctx = self.with_context(_sale_order_create=True)
        return super(SaleOrder, self_ctx).create(vals)

    @api.multi
    def write(self, vals):
        self_ctx = self.with_context(_sale_order_write=True)
        return super(SaleOrder, self_ctx).write(vals)

    @job(default_channel='root.esb')
    def ws_create_new(self, data):
        """Create a sale order with data coming from webservices."""
        try:
            return self.with_context(
                no_connector_export=True
            )._ws_create_new(data)
        except IntegrityError as error:
            self.env.cr.rollback()
            _logger.error('Webservice create saleorder, integrity error : %s',
                          error)
            raise

    def _ws_create_new(self, data):
        order_data = self._ws_create_order_data(data)
        order_data = self.env['sale.order'].play_onchanges(
            order_data,
            ['discount_pricelist_id',
             'supplier_promotion_allowed',
             'partner_id',
             'team_id',
             ],
            )
        order = self.create(order_data)

        for line in self._ws_create_order_line_data(data)[:]:
            line['order_id'] = order.id
            changed_line = self.env['sale.order.line'].play_onchanges(
                line,
                ['product_id'],
            )
            self.env['sale.order.line'].create(changed_line)

        order.action_confirm_background()
        return order

    def _ws_get_partner(self, ref):
        partner = self.env['res.partner'].search([
            ('ref', '=', ref),
            ('parent_id', '=', False),
        ])
        if not partner:
            raise exceptions.MissingError(
                _("No match found for customer_id: %s") % ref
            )
        elif len(partner) != 1:
            raise exceptions.MissingError(
                _("Several partners found for customer_id: %s") % ref
            )
        return partner

    def _ws_create_order_data(self, data):
        order_data = {}
        partner_ref = data['customer_id']
        partner = self._ws_get_partner(partner_ref)
        order_data['team_id'] = self.env.ref(
                'sales_team.salesteam_website_sales').id
        order_data['esb_ref'] = data['increment_id']
        order_data['partner_id'] = partner.id
        # We do not use the date coming from the web service because
        # it does not have a time part
        order_data['date_order'] = fields.datetime.now()
        order_data['client_order_ref'] = data['order_ref']
        order_data['partner_invoice_id'] = partner.id
        order_data['state'] = 'draft'
        if 'carrier_id' in data:
            carrier = self.env['delivery.carrier'].search([
                ('esb_ref', '=', data['carrier_id'])]).exists()
            if len(carrier):
                order_data['carrier_id'] = carrier.id
            else:
                _logger.error('Webservice new saleorder, carrier %s not found',
                              data['carrier_id'])
        elif partner.property_delivery_carrier_id:
            order_data['carrier_id'] = partner.property_delivery_carrier_id.id
        return order_data

    def _ws_create_order_line_data(self, data):
        lines = []
        for line in data['lines']:
            if line.get('free'):
                # free line, skip it
                continue
            product = self.env['product.product'].search([
                ('default_code', '=', line['sku'])])

            if len(product) > 1:
                message = ('Webservice new saleorder, several'
                           ' products with the same sku %s found')
                _logger.error(message, line['sku'])
                raise exceptions.UserError(_(message) % line['sku'])

            elif not len(product):
                message = 'Webservice new saleorder, product %s not found'
                _logger.error(message, line['sku'])
                raise exceptions.UserError(_(message) % line['sku'])

            else:
                sol = {}
                sol['product_id'] = product.id
                sol['name'] = product.name
                sol['product_uom'] = product.uom_id.id
                sol['product_uom_qty'] = line.pop('quantity')
                sol['price_unit'] = product.list_price
                sol['discounting_type'] = 'multiplicative'
                sol['esb_ref'] = line.pop('line_id')
                lines.append(sol)

        return lines
