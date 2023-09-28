# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.account.models.account_move import AccountMove
from odoo.addons.account.models.account_move_line import (
    AccountMoveLine as AccountMoveLineBase,
)


class AccountMoveLine(AccountMoveLineBase):

    globalization_move_id = fields.Many2one[AccountMove](
        readonly=True,
        help="Technical field used for payment globalization reconciliation",
    )
