# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import fields
from odoo.osv.expression import AND

from odoo.addons.account.models.partner import ResPartner as ResPartnerBase


class ResPartner(ResPartnerBase):

    total_invoiced_in_current_fiscal_year = fields.Monetary(
        compute="_compute_invoice_total_current_fiscal_year",
        string="Total Invoiced during the current fiscal year",
        groups="account.group_account_invoice",
        currency_field="currency_id",
    )

    def _get_fiscal_year(self):
        today = fields.Date.today()
        current_year = today.year
        if today <= date(year=current_year, month=9, day=30):
            start_date_fiscal_year = date(year=current_year - 1, month=10, day=1)
            end_date_fiscal_year = date(year=current_year, month=9, day=30)
        else:
            start_date_fiscal_year = date(year=current_year, month=10, day=1)
            end_date_fiscal_year = date(year=current_year + 1, month=9, day=30)
        return start_date_fiscal_year, end_date_fiscal_year

    def _compute_invoice_total_current_fiscal_year(self):
        account_invoice_report = self.env["account.invoice.report"]
        start_date_fiscal_year, end_date_fiscal_year = self._get_fiscal_year()
        for rec in self:
            total_invoiced_in_current_fiscal_year = 0
            all_child = self.with_context(active_test=False).search(
                [("id", "child_of", rec.ids)]
            )
            group = account_invoice_report.read_group(
                [
                    ("partner_id", "in", all_child.ids),
                    ("state", "=", "posted"),
                    ("move_type", "in", ("out_invoice", "out_refund")),
                    "&",
                    ("invoice_date", ">=", start_date_fiscal_year),
                    ("invoice_date", "<=", end_date_fiscal_year),
                ],
                ["price_subtotal:sum"],
                ["commercial_partner_id"],
            )
            if group and isinstance(group, list):
                total_invoiced_in_current_fiscal_year = group[0].get(
                    "price_subtotal", 0
                )
            rec.total_invoiced_in_current_fiscal_year = (
                total_invoiced_in_current_fiscal_year
            )

    def action_view_partner_invoices(self):
        """This function returns an action that display invoices/refunds made for the given partners."""

        start_date_fiscal_year, end_date_fiscal_year = self._get_fiscal_year()

        action = super().action_view_partner_invoices()
        action["domain"] = AND(
            [
                action["domain"],
                [
                    ("invoice_date", ">=", start_date_fiscal_year),
                    ("invoice_date", "<=", end_date_fiscal_year),
                ],
            ]
        )
        return action
