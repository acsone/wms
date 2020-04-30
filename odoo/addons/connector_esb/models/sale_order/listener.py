# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if
from odoo.addons.queue_job.job import identity_exact


class SaleExportListener(Component):
    _name = 'esb.sale.order.export.listener'
    _inherit = 'base.connector.listener'
    _apply_on = ['sale.order']

    EXPORT_DESCRIPTION = u"Export sale order {} to ESB's webservice"

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        if not record.esb_is_exportable():
            return
        record.with_delay(
            description=self.EXPORT_DESCRIPTION.format(record.name or ''),
            identity_key=identity_exact,
            priority=25,
        ).esb_export_record()

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        if not record.esb_is_exportable():
            return
        if record.env.context.get('_sale_order_create'):
            # export already triggered by the sale order create
            return
        record.with_delay(
            description=self.EXPORT_DESCRIPTION.format(record.name),
            identity_key=identity_exact,
            priority=25,
        ).esb_export_record()


class SaleLineExportListener(Component):
    _name = 'esb.sale.order.line.export.listener'
    _inherit = 'base.connector.listener'
    _apply_on = ['sale.order.line']

    EXPORT_DESCRIPTION = u"Export sale order {} to ESB's webservice"

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        if not record.order_id.esb_is_exportable():
            return
        if record.env.context.get(
            '_sale_order_create'
        ) or record.env.context.get('_sale_order_write'):
            # export already triggered by the sale order write/create
            return
        if set(fields) & {
            'qty_delivered',
            'product_qty_unavailable',
            'product_qty_canceled',
        }:
            so = record.order_id
            so.with_delay(
                description=self.EXPORT_DESCRIPTION.format(so.name or ''),
                identity_key=identity_exact,
                priority=25,
            ).esb_export_record()
