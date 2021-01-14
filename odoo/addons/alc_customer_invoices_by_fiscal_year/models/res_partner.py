# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    total_invoiced_in_current_fiscal_year = fields.Monetary(
        compute="_compute_invoice_total_current_fiscal_year",
        string="Total Invoiced during the current fiscal year",
        groups="account.group_account_invoice",
    )

    def _get_fiscal_year(self):
        today = datetime.today().strftime("%Y-%m-%d")
        current_year = today.split("-")[0]
        if today <= current_year + "-09-30":
            start_date_fiscal_year = str(int(today.split("-")[0]) - 1) + "-10-01"
            end_date_fiscal_year = current_year + "-09-30"
        if today >= current_year + "-10-01":
            start_date_fiscal_year = today.split("-")[0] + "-10-01"
            end_date_fiscal_year = str(int(today.split("-")[0]) + 1) + "-09-30"
        return start_date_fiscal_year, end_date_fiscal_year

    @api.multi
    def _compute_invoice_total_current_fiscal_year(self):
        account_invoice_report = self.env["account.invoice.report"]

        start_date_fiscal_year, end_date_fiscal_year = self._get_fiscal_year()

        if not self.ids:
            return True

        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self:
            all_partners_and_children[partner] = (
                self.with_context(active_test=False)
                .search([("id", "child_of", partner.id)])
                .ids
            )
            all_partner_ids += all_partners_and_children[partner]

        # generate where clause to include multicompany rules
        where_query = account_invoice_report._where_calc(
            [
                ("partner_id", "in", all_partner_ids),
                ("state", "not in", ["draft", "cancel"]),
                ("type", "in", ("out_invoice", "out_refund")),
                "&",
                ("date", ">=", start_date_fiscal_year),
                ("date", "<=", end_date_fiscal_year),
            ]
        )
        account_invoice_report._apply_ir_rules(where_query, "read")
        from_clause, where_clause, where_clause_params = where_query.get_sql()

        # price_total is in the company currency
        query = (
            """
                  SELECT SUM(price_total) as total, partner_id
                    FROM account_invoice_report account_invoice_report
                   WHERE %s
                   GROUP BY partner_id
                """
            % where_clause
        )
        self.env.cr.execute(query, where_clause_params)  # pylint: disable=E8103
        price_totals = self.env.cr.dictfetchall()
        for partner, child_ids in all_partners_and_children.items():
            partner.total_invoiced_in_current_fiscal_year = sum(
                price["total"]
                for price in price_totals
                if price["partner_id"] in child_ids
            )

    def open_partner_history(self):
        """
        This function returns an action that display invoices/refunds made for the given partners.
        """

        start_date_fiscal_year, end_date_fiscal_year = self._get_fiscal_year()

        action = super(ResPartner, self).open_partner_history()

        action["domain"].append("&")
        action["domain"].append(("date_invoice", ">=", start_date_fiscal_year))
        action["domain"].append(("date_invoice", "<=", end_date_fiscal_year))
        return action
