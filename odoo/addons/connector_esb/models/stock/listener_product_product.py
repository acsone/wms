# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.component_event import skip_if
from odoo.addons.queue_job.job import identity_exact


class ProductProductListener(Component):
    """ Listen to the creation of a product.

    When detected, requests an export of the product.

    The listener on the update is set on the product_template model,
    because the fields that are of interest to us are there and the
    update on product_product is never called.
    """

    _name = "esb.product.product.export.listener"
    _inherit = "base.connector.listener"
    _apply_on = ["product.product"]

    EXPORT_DESCRIPTION = u"Export product {} stock state change to ESB"

    @skip_if(lambda self, record, **kwargs: self.no_connector_export(record))
    def on_record_create(self, record, fields=None):
        if not record._is_product_fit_to_export():
            return
        product_code = record.default_code or ""
        record.with_delay(
            description=self.EXPORT_DESCRIPTION.format(product_code),
            identity_key=identity_exact,
            priority=25,
        ).esb_export_record(
            timestamp=self.env.ref("connector_esb.esb_timestamp_stock_update_single")
        )
