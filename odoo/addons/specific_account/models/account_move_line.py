# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _create(self, vals):
        """
        By default, each time you create an account.move.line, Odoo will
        recompute the value for the total amount and the matched_percentage
        on the account.move with all lines. This step is time consuming.

        To incrase the creation of the inital customer/supplier balance,
        we disable the computation of these field.
        We will manually call these method after the import of the initial
        balance.
        """
        if not self._context.get("import_initial_balance"):
            return super(AccountMoveLine, self)._create(vals)

        # Call super without recompute methods
        with self.env.norecompute():
            result = super(AccountMoveLine, self)._create(vals)

        # Remove the recompute method for matched_percentage and amount
        AccountMove = self.env["account.move"]
        matched_percentage = AccountMove._fields["matched_percentage"]
        amount = AccountMove._fields["amount"]

        if matched_percentage in self.env.all.todo:
            del self.env.all.todo[matched_percentage]

        if amount in self.env.all.todo:
            del self.env.all.todo[amount]

        # Call the method recompute
        self.recompute()

        return result
