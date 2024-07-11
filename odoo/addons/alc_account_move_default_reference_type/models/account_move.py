# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.account_payment_order.models.account_move import (
    AccountMove as AccountMoveBase,
)


class AccountMove(AccountMoveBase):

    reference_type = fields.Selection(compute="_compute_reference_type", store=True)

    @api.depends("commercial_partner_id")
    def _compute_reference_type(self):
        for rec in self:
            if (
                rec.commercial_partner_id
                and rec.commercial_partner_id.out_inv_comm_type
            ):
                rec.reference_type = rec.commercial_partner_id.out_inv_comm_type
            else:
                rec.reference_type = "none"
