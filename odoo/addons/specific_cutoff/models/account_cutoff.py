# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models


class AccountCutoff(models.Model):
    _inherit = "account.cutoff"

    @api.model
    def _cron_cutoff_refund(self, type):
        invoices = self.env["account.invoice"].search(
            [
                ("state", "in", ("draft", "proforma2")),
                ("type", "=", type),
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
            .with_context(active_model=invoices[0]._name, active_ids=invoices.ids)
            .create({"date": last_day})
        )
        wizard.action_accrue()

    @api.model
    def _cron_cutoff_expense_refund(self):
        self._cron_cutoff_refund("in_refund")

    @api.model
    def _cron_cutoff_revenue_refund(self):
        self._cron_cutoff_refund("out_refund")

    def get_lines(self):
        self.ensure_one()
        if self.type == "accrued_expense":
            # Exclude blocked purchases
            self.line_ids.unlink()
            SaleOrderLine = self.env["purchase.order.line"]
            with SaleOrderLine._auto_join(["order_id"]):
                lines = self.env["purchase.order.line"].search(
                    [("qty_to_invoice", "!=", 0), ("order_id.state", "!=", "done")]
                )
            for line in lines:
                self.env["account.cutoff.line"].create(self._prepare_line(line))
        else:
            return super(AccountCutoff, self).get_lines()
