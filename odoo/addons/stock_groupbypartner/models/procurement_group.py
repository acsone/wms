# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    carrier_id = fields.Many2one(
        comodel_name="delivery.carrier", string="Delivery Method"
    )
