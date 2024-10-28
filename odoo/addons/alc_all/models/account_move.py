# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import drop_index, index_exists

from odoo.addons.account.models import account_move


class AccountMove(account_move.AccountMove):

    def init(self):  # pylint: disable=missing-return
        super().init()
        if index_exists(
            self._cr,
            "account_move_payment_idx",
        ):
            # covered by the previous index
            drop_index(self._cr, "account_move_journal_id_manidx", "account_move")
