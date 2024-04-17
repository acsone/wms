# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields

from odoo.addons.account.models.account_move_line import AccountMoveLine as MoveLine


class AccountMoveLine(MoveLine):

    date_maturity = fields.Date(
        compute="_compute_date_maturity",
        readonly=False,
        store=True,
    )

    @api.depends("date")
    def _compute_date_maturity(self):
        """
        If maturity date is not set, use the move date for value if the.

        journal property 'use_move_date_as_date_maturity' is enabled.
        """
        for line in self:
            if (
                not line.date_maturity
                and line.date
                and line.move_id.journal_id.use_move_date_as_date_maturity
            ):
                line.date_maturity = line.date
