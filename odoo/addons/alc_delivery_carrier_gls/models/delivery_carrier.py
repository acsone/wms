# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("gls", "Gls")])

    @api.multi
    def gls_get_shipping_price_from_so(self, order):
        self.ensure_one()
        try:
            price_unit = self.get_price_available(order)
            self.available = True
        except UserError as e:
            # No suitable delivery method found, probably configuration error
            _logger.exception("Carrier %s: %s", self.name, e.name)
            price_unit = 0.0
        if order.company_id.currency_id.id != order.pricelist_id.currency_id.id:
            price_unit = order.company_id.currency_id.with_context(
                date=order.date_order
            ).compute(price_unit, order.pricelist_id.currency_id)

        return [price_unit * (1.0 + (float(self.margin) / 100.0))]

    @api.multi
    def gls_send_shipping(self, pickings):
        return [{"exact_price": False, "tracking_number": False}]

    @api.multi
    def gls_get_tracking_link(self, pickings):
        return False

    @api.multi
    def gls_cancel_shipment(self, pickings):
        return False
