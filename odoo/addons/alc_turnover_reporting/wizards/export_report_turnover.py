# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import io
from datetime import datetime

import numpy as np
import pandas as pd
from odoo import api, fields, models


class ExportReportTurnover(models.TransientModel):

    _name = "export.report.turnover"

    name = fields.Char("File Name", readonly=True, default="report_compta.xlsx")
    data = fields.Binary("File", readonly=True)

    state = fields.Selection(
        [("choose", "choose"), ("get", "get")],  # choose language or get the file
        default="choose",
    )

    @api.multi
    def get_export_data(self):
        this = self[0]
        self.env.cr.execute(
            """
                SELECT
                date_trunc('month', sm.date) as date,
                SUM((sol.price_subtotal/sol.product_uom_qty) * sm.product_qty) AS debit_from_sm FROM stock_move sm
                JOIN sale_order_line sol ON sol.id = sm.order_line_id
                JOIN stock_location from_loc ON from_loc.id = sm.location_id
                WHERE sm.state = 'done' AND from_loc.usage = 'customer' AND sol.product_uom_qty != 0  AND sm.product_id=sol.product_id
                GROUP BY date_trunc('month', sm.date)
        """
        )

        result = self.env.cr.fetchall()
        debit_from_sm_df = pd.DataFrame(result, columns=["date", "debit_from_sm"])

        self.env.cr.execute(
            """
                SELECT
                date_trunc('month', sm.date) as date,
                SUM((sol.price_subtotal/sol.product_uom_qty) * sm.product_qty) AS credit_from_sm FROM stock_move sm
                JOIN sale_order_line sol ON sol.id = sm.order_line_id
                JOIN stock_location to_loc ON to_loc.id = sm.location_dest_id
                WHERE sm.state = 'done' AND to_loc.usage = 'customer' AND sol.product_uom_qty != 0 AND sm.product_id=sol.product_id
                GROUP BY date_trunc('month', sm.date)
        """
        )

        result2 = self.env.cr.fetchall()
        credit_from_sm_df = pd.DataFrame(result2, columns=["date", "credit_from_sm"])

        credit_debit_from_sm_df = pd.merge(
            credit_from_sm_df, debit_from_sm_df, on="date"
        )

        credit_debit_from_sm_df["balance_from_sm"] = (
            credit_debit_from_sm_df["debit_from_sm"]
            - credit_debit_from_sm_df["credit_from_sm"]
        )
        credit_debit_from_sm_df["date"] = pd.DatetimeIndex(
            credit_debit_from_sm_df["date"]
        )
        credit_debit_from_sm_by_year = credit_debit_from_sm_df.groupby(
            credit_debit_from_sm_df["date"].dt.year
        ).sum()
        credit_debit_from_sm_by_year.reset_index(inplace=True)
        credit_debit_from_sm_by_year.rename(columns={"date": "year"}, inplace=True)

        credit_debit_from_invoicing = (
            self.env["account.move.line"]
            .with_context(lang="en_US")
            .read_group(
                [
                    (
                        "account_id.tag_ids",
                        "=",
                        self.env.ref("__import__.account_account_tag_alcyn_pp-100").id,
                    )
                ],
                ["debit", "credit", "balance", "date", "company_id"],
                ["date:month", "company_id"],
                lazy=False,
            )
        )
        credit_debit_from_invoicing_df = pd.DataFrame(credit_debit_from_invoicing)
        credit_debit_from_invoicing_df = credit_debit_from_invoicing_df.drop(
            ["__count", "__domain", "company_id"], axis=1
        ).rename(
            columns={
                "balance": "balance_from_invoicing",
                "credit": "credit_from_invoicing",
                "debit": "debit_from_invoicing",
                "date:month": "date",
            }
        )

        # Dates formatting
        dates_formated = credit_debit_from_invoicing_df.apply(
            lambda row: datetime.strptime(row["date"], "%B %Y"), axis=1
        )
        credit_debit_from_invoicing_df["date"] = pd.DatetimeIndex(dates_formated)
        credit_debit_from_invoicing_by_year = credit_debit_from_invoicing_df.groupby(
            credit_debit_from_invoicing_df["date"].dt.year
        ).sum()
        credit_debit_from_invoicing_by_year.reset_index(inplace=True)
        credit_debit_from_invoicing_by_year.rename(
            columns={"date": "year"}, inplace=True
        )

        credit_debit_balance = pd.merge(
            credit_debit_from_invoicing_df,
            credit_debit_from_sm_df,
            on="date",
            how="outer",
        )
        credit_debit_balance["diff_credit"] = (
            credit_debit_balance["credit_from_invoicing"]
            - credit_debit_balance["credit_from_sm"]
        )
        credit_debit_balance["diff_debit"] = (
            credit_debit_balance["debit_from_invoicing"]
            - credit_debit_balance["debit_from_sm"]
        )
        credit_debit_balance["diff_balance"] = (
            credit_debit_balance["balance_from_invoicing"]
            - credit_debit_balance["balance_from_sm"]
        )
        cols = [
            "date",
            "credit_from_sm",
            "credit_from_invoicing",
            "diff_credit",
            "debit_from_sm",
            "debit_from_invoicing",
            "diff_debit",
            "balance_from_sm",
            "balance_from_invoicing",
            "diff_balance",
        ]
        credit_debit_balance = credit_debit_balance[cols]

        credit_debit_balance_by_year = pd.merge(
            credit_debit_from_invoicing_by_year,
            credit_debit_from_sm_by_year,
            on="year",
            how="outer",
        )
        credit_debit_balance_by_year["diff_credit"] = (
            credit_debit_balance_by_year["credit_from_invoicing"]
            - credit_debit_balance_by_year["credit_from_sm"]
        )
        credit_debit_balance_by_year["diff_debit"] = (
            credit_debit_balance_by_year["debit_from_invoicing"]
            - credit_debit_balance_by_year["debit_from_sm"]
        )
        credit_debit_balance_by_year["diff_balance"] = (
            credit_debit_balance_by_year["balance_from_invoicing"]
            - credit_debit_balance_by_year["balance_from_sm"]
        )
        cols = [
            "year",
            "credit_from_sm",
            "credit_from_invoicing",
            "diff_credit",
            "debit_from_sm",
            "debit_from_invoicing",
            "diff_debit",
            "balance_from_sm",
            "balance_from_invoicing",
            "diff_balance",
        ]
        credit_debit_balance_by_year = credit_debit_balance_by_year[cols]

        # count business days
        year_1 = credit_debit_balance_by_year["year"] - 1
        credit_debit_balance_by_year.insert(1, "year-1", year_1)
        credit_debit_balance_by_year["year-1"] = credit_debit_balance_by_year[
            "year-1"
        ].astype(str)
        credit_debit_balance_by_year["year"] = credit_debit_balance_by_year[
            "year"
        ].astype(str)
        business_days = credit_debit_balance_by_year.apply(
            lambda row: np.busday_count(row["year-1"], row["year"]), axis=1
        )
        credit_debit_balance_by_year.insert(2, "busdays", business_days)

        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        credit_debit_balance.to_excel(writer, sheet_name="reportByMonths")
        credit_debit_balance_by_year.to_excel(writer, sheet_name="reportByYears")

        # Format excel to something nice
        workbook = writer.book
        worksheet1 = writer.sheets["reportByMonths"]
        worksheet2 = writer.sheets["reportByYears"]
        formatSheet = workbook.add_format({"num_format": "0.00"})
        worksheet1.set_column("B:K", 30, formatSheet)
        worksheet2.set_column("B:M", 30, formatSheet)
        writer.save()

        excel_data = output.getvalue()
        data = base64.b64encode(excel_data)

        this.write({"state": "get", "data": data, "name": "report_compta.xlsx"})
        return {
            "type": "ir.actions.act_window",
            "res_model": "export.report.turnover",
            "view_mode": "form",
            "view_type": "form",
            "res_id": this.id,
            "views": [(False, "form")],
            "target": "new",
        }
