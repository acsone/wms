# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.rma_reason.models.rma_reason import RmaReason as RmaReasonBase


class RmaReason(RmaReasonBase):
    charge_restocking_fee = fields.Boolean(
        help="Tick this box if you wish to charge your customer a fee in "
        "case of return of goods",
        default=False,
    )
