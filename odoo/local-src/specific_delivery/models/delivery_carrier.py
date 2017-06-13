# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_vehicle_id = fields.Many2one(
        comodel_name='round.vehicle',
        string='Delivery vehicle',
    )
