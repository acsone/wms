# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.account.models import account_move


class AccountMove(account_move.AccountMove):
    @api.depends("state")
    def _compute_payment_reference(self):
        return super()._compute_payment_reference()
