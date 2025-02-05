# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.account.models.account_analytic_account import (
    AccountAnalyticAccount as AnalyticAccount,
)
from odoo.addons.account.models.account_move_line import AccountMoveLine as MoveLine


class AccountMoveLine(MoveLine):

    analytic_account_id = fields.Many2one[AnalyticAccount](
        string="Analytic Account",
        compute="_compute_analytic_account_id",
        store=True,
        index=True,
    )

    @api.depends("analytic_distribution")
    def _compute_analytic_account_id(self):
        # analytic_distribution is a json field
        for rec in self:
            account_id = False
            if rec.analytic_distribution:
                key = next(iter(rec.analytic_distribution.keys()))
                if isinstance(key, str) and key.isnumeric():
                    account_id = int(key)
            rec.analytic_account_id = account_id
