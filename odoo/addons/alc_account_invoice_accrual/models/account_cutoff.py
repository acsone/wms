# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api

from odoo.addons.account_cutoff_base.models.account_cutoff import (
    AccountCutoff as AccountCutoffBase,
)


class AccountCutoff(AccountCutoffBase):
    @api.model
    def _cron_cutoff_refund(self, move_type):
        invoices = self.env["account.move"].search(
            [
                ("state", "=", "draft"),
                ("move_type", "=", move_type),
                ("accrual_move_id", "=", False),
            ]
        )
        if not invoices:
            return
        # Cron is expected to run at begin of new period. We need the last day
        # of previous month. Support some time difference and compute last day
        # of previous period.
        last_day = datetime.today()
        if last_day.day > 20:
            last_day += relativedelta(months=1)
        last_day = last_day.replace(day=1)
        last_day -= relativedelta(days=1)
        wizard = (
            self.env["account.move.accrue"]
            .with_context(active_model="account.move", active_ids=invoices.ids)
            .create({"date": last_day})
        )
        wizard.action_accrue()

    @api.model
    def _cron_cutoff_expense_refund(self):
        self._cron_cutoff_refund("in_refund")

    @api.model
    def _cron_cutoff_revenue_refund(self):
        self._cron_cutoff_refund("out_refund")
