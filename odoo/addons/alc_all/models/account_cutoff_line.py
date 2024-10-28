# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import drop_index, index_exists

from odoo.addons.account_cutoff_base.models import account_cutoff_line


class AccountCutOffLine(account_cutoff_line.AccountCutoffLine):

    def init(self):  # pylint: disable=missing-return
        super().init()
        if index_exists(
            self._cr,
            "account_cutoff_line_origin_move_line_id_index",
        ):
            # duplicate of the previous index
            drop_index(
                self._cr,
                "account_cutoff_line_origin_move_line_id_idx",
                "account_cutoff_line",
            )
