# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.account.models.account_journal import AccountJournal as Journal


class AccountJournal(Journal):

    use_move_date_as_date_maturity = fields.Boolean(
        help="Check this if you want to fill in a maturity date on moves that"
        " use this journal and if no maturity date is defined. The date will be"
        " in that case the move date."
    )
