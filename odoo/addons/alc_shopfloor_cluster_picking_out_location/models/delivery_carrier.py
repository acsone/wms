# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class DeliveryCarrier(models.Model):

    _inherit = "delivery.carrier"
    unload_on_specific_location = fields.Boolean(
        string="Unload packs in specific OUT locations",
        default=True,
        help="If you tick this box, you will have to unload"
        " your packs into specific out locations.",
    )
