# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if
from odoo.addons.queue_job.job import identity_exact


class ProductTemplateListener(Component):
    """ Listen to changes on some fields of product.

    When detected, requests an export of the product.

    The listener on create is set on the product_product model,
    because when set on product_template the event is triggered when
    the field product_variant_id is not yet set, so we do not have
    the product_product record to export.
    """

    _name = 'esb.product.template.export.listener'
    _inherit = 'base.connector.listener'
    _apply_on = ['product.template']

    EXPORT_DESCRIPTION = u"Export product {} stock state change to ESB"

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_write(self, record, fields=None):
        if record.env.context.get('_product_create'):
            # Export already triggered by the product create
            return
        if not record.product_variant_id._is_product_fit_to_export():
            return
        if 'state_id' in fields:
            product_code = record.default_code or ''
            record.product_variant_id.with_delay(
                description=self.EXPORT_DESCRIPTION.format(product_code),
                identity_key=identity_exact,
                priority=25,
            ).esb_export_record(
                timestamp=self.env.ref(
                    'connector_esb.esb_timestamp_stock_update_single'
                )
            )
