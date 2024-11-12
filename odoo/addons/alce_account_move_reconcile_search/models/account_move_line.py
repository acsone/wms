# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.account.models.account_move_line import (
    AccountMoveLine as AccountMoveLineBase,
)


class AccountMoveLine(AccountMoveLineBase):

    name = fields.Char(index="trigram", unaccent=False)
    ref = fields.Char(index="trigram", unaccent=False)
