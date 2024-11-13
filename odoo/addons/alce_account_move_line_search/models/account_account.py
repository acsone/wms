# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.account.models.account_account import (
    AccountAccount as AccountAccountBase,
)


class AccountAccount(AccountAccountBase):
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self.env["account.root"].refresh_materialized_view()
        return res

    def write(self, vals):
        res = super().write(vals)
        self.env["account.root"].refresh_materialized_view()
        return res

    def unlink(self):
        res = super().unlink()
        self.env["account.root"].refresh_materialized_view()
        return res
