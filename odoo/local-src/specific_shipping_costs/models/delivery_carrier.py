# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    compute_shipping_costs_on_invoice = fields.Boolean(
        string='Compute shipping costs on invoice',
    )
    esb_ref = fields.Char(
        string='Reference for ESB'
    )
