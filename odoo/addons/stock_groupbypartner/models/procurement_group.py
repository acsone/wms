# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    carrier_id = fields.Many2one(
        comodel_name="delivery.carrier",
        string="Delivery Method",
        help="The partner shipping on the SO",
    )
    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        help="The partner customer on the SO. In the same time, the partner_id "
        "is the partner_shipping_id from the SO. This fiels help us to "
        "keep the information of the real/final customer from the SO",
    )
