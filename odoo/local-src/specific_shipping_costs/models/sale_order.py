# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    compute_shipping_costs_on_invoice = fields.Boolean(
        related='carrier_id.compute_shipping_costs_on_invoice',
        readonly=True,
    )

    def _create_delivery_line(self, carrier, price_unit):
        if not self.compute_shipping_costs_on_invoice:
            super(SaleOrder, self)._create_delivery_line(carrier, price_unit)
