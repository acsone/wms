# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_picking import PickingType


class StockPickingType(PickingType):

    no_expired_reservation_allowed = fields.Boolean(
        string="Disallow Expired Lot Reservations",
        help="Check this box to enforce a policy that prevents reservations for lots "
        "that have already expired. When enabled, users won't be able to make "
        "reservations for lots whose expiration date has passed.",
    )
