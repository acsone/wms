# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.delivery.models import delivery_carrier


class DeliveryCarrier(delivery_carrier.DeliveryCarrier):

    available_in_website = fields.Boolean(
        default=False,
        help="If true, this carrier will be available in the list of available "
        "carriers in the website at checkout.",
    )
