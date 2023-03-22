# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.delivery.models import delivery_carrier


class DeliveryCarrier(delivery_carrier.DeliveryCarrier):

    is_long_term_delivery = fields.Boolean(
        string="Long time delivery",
        default=False,
        help="Check to avoid purge for too long delivery",
    )
