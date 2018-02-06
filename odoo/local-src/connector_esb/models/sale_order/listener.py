# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if


class SaleExportListener(Component):
    _name = 'esb.sale.order.export.listener'
    _inherit = 'base.connector.listener'
    _apply_on = ['sale.order']

    EXPORT_DESCRIPTION = "Export a sales order to ESB's webservice"

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        record.with_delay(
            description=self.EXPORT_DESCRIPTION
        ).esb_export_record()

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        record.with_delay(
            description=self.EXPORT_DESCRIPTION
        ).esb_export_record()
