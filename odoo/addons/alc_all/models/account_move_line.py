# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import index_exists

from odoo.addons.account.models.account_move_line import (
    AccountMoveLine as AccountMoveLineBase,
)


class AccountMoveLine(AccountMoveLineBase):
    """Create this index manually as the foreign key decreases performances on DELETE."""

    def init(self):  # pylint: disable=missing-return
        super().init()
        if not index_exists(
            self._cr,
            "account_account_tag_account_move_line_account_move_line_id_fkey_idx",
        ):
            self._cr.execute(
                """
                CREATE INDEX account_account_tag_account_move_line_account_move_line_id_fkey_idx
                ON
                    account_account_tag_account_move_line_rel (account_move_line_id)
                """
            )
