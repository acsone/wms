# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.rma.models.rma_operation import RmaOperation as RmaOperationBase


class RmaOperation(RmaOperationBase):
    duplicate_delivery_slip_at_reception = fields.Boolean(
        string="Duplicate Delivery Slip at reception",
        default=False,
        help="Check this box to print the delivery slip as a 'DUPLICATA' "
        "(duplicate copy) at reception.",
    )
