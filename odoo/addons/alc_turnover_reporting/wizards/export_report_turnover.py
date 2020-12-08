# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import io
from datetime import datetime

from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ExportReportTurnover(models.TransientModel):

    _name = "export.report.turnover"

    name = fields.Char("File Name", readonly=True, default="report_compta.xlsx")
    data = fields.Binary("File", readonly=True)

    state = fields.Selection(
        [("choose", "choose"), ("get", "get")],  # choose language or get the file
        default="choose",
    )

    def _sql_data_to_dataframe(self, data, column_names):
        return pd.DataFrame(data, columns=column_names)

    def _get_data_from_stock_moves(self, in_or_out_move, groupby_type):
        if in_or_out_move == "out_move":
            self.env.cr.execute(
                """
                    SELECT
                    date_trunc(%(groupby_type)s, sm.date) as date,
                    SUM((sol.price_subtotal/sol.product_uom_qty) * sm.product_qty) AS debit_from_sm FROM stock_move sm
                    JOIN sale_order_line sol ON sol.id = sm.order_line_id
                    JOIN stock_location from_loc ON from_loc.id = sm.location_id
                    WHERE sm.state = 'done' AND from_loc.usage = 'customer' AND sol.product_uom_qty != 0  AND sm.product_id=sol.product_id
                    GROUP BY date_trunc(%(groupby_type)s, sm.date)
            """,
                {"groupby_type": groupby_type},
            )

        if in_or_out_move == "in_move":
            self.env.cr.execute(
                """
                    SELECT
                    date_trunc(%(groupby_type)s, sm.date) as date,
                    SUM((sol.price_subtotal/sol.product_uom_qty) * sm.product_qty) AS credit_from_sm FROM stock_move sm
                    JOIN sale_order_line sol ON sol.id = sm.order_line_id
                    JOIN stock_location to_loc ON to_loc.id = sm.location_dest_id
                    WHERE sm.state = 'done' AND to_loc.usage = 'customer' AND sol.product_uom_qty != 0 AND sm.product_id=sol.product_id
                    GROUP BY date_trunc(%(groupby_type)s, sm.date)
            """,
                {"groupby_type": groupby_type},
            )

        return self.env.cr.fetchall()

    def _get_data_from_invoicing(self, groupby_type):

        return (
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
                [groupby_type, "company_id"],
                lazy=False,
            )
        )

    def _compute_CA_balance(self, credit, debit):
        return -(debit - credit)

    def _compute_mensual_grow(self, data, today):
        # data["Turnover (prev. Month)"] = (
        #     data["Turnover (stock moves)"].shift(12).fillna(0)
        # )
        data.insert(
            2, "Turnover (prev. Month)", data["Turnover (stock moves)"].shift(12)
        )
        data.insert(6, "Business days (prev. Month)", data["Business days"].shift(12))
        # data["Business days (prev. Month)"] = (
        #     data["Business days"].shift(12).fillna(0)
        # )

        data["Mensual grow"] = (
            (data["Turnover (stock moves)"] - data["Turnover (prev. Month)"])
            / data["Turnover (prev. Month)"]
        ) * 100
        data.loc[~np.isfinite(data["Mensual grow"]), "Mensual grow"] = np.nan

        # For unfinished month, specific treatment
        if data["Month+1"].iloc[-1] == today:
            # grow = (CA_current_month - (CA_same_month_previous_year/business_days_month_prev_year)*business_days_current_month) /
            #           ((CA_same_month_previous_year/business_days_month_prev_year)*business_days_current_month)
            data["Mensual grow"].iloc[-1] = (
                (
                    data["Turnover (stock moves)"].iloc[-1]
                    - (
                        data["Turnover (prev. Month)"].iloc[-1]
                        / data["Business days (prev. Month)"].iloc[-1]
                    )
                    * data["Business days"].iloc[-1]
                )
                / (
                    (
                        data["Turnover (prev. Month)"].iloc[-1]
                        / data["Business days (prev. Month)"].iloc[-1]
                    )
                    * data["Business days"].iloc[-1]
                )
            ) * 100

    def _compute_global_grow(self, data_by_years, data_by_months, today):
        data_by_years["Turnover (prev. Year)"] = (
            data_by_years["Turnover (stock moves)"].shift(1).fillna(0)
        )
        data_by_years["Business days (prev. Year)"] = (
            data_by_years["Business days"].shift(1).fillna(0)
        )

        data_by_years["Global grow"] = (
            (
                data_by_years["Turnover (stock moves)"]
                - data_by_years["Turnover (prev. Year)"]
            )
            / data_by_years["Turnover (prev. Year)"]
        ) * 100
        data_by_years.loc[
            ~np.isfinite(data_by_years["Global grow"]), "Global grow"
        ] = np.nan
        if data_by_months["Month+1"].iloc[-1] == today:

            # If unfinished month : get the info from the month in the previous year
            current_month = today.split("-")[1]
            last_year = int(today.split("-")[0]) - 1
            date_to_get = str(last_year) + "-" + current_month + "-01"
            same_month_last_year = pd.DataFrame()
            same_month_last_year["bool"] = data_by_months["Month"].eq(date_to_get)
            index = same_month_last_year[same_month_last_year["bool"]].index.values

            if index:
                start_year = str(last_year) + "-01-01"
                last_year = pd.DataFrame()
                last_year["bool"] = data_by_months["Month"].eq(start_year)
                index_start = last_year[last_year["bool"]].index.values

                correction_factor = (
                    data_by_months["Turnover (stock moves)"]
                    .iloc[index_start[0] : index[0]]
                    .sum()
                    + data_by_months["Turnover (stock moves)"].iloc[index[0]]
                    / data_by_months["Business days"].iloc[index[0]]
                    * data_by_months["Business days"].iloc[-1]
                )
                data_by_years["Global grow"].iloc[-1] = (
                    (
                        data_by_years["Turnover (stock moves)"].iloc[-1]
                        - correction_factor
                    )
                    / correction_factor
                ) * 100

    def _count_business_days(self, data, start_date_name, end_date_name, today):
        # count business days
        if start_date_name == "Month":
            data[end_date_name] = data[start_date_name].dt.date + relativedelta(
                months=1
            )
            data[end_date_name] = data[end_date_name].astype(str)
            data[start_date_name] = data[start_date_name].astype(str)
        elif start_date_name == "Year":
            data[end_date_name] = data[start_date_name] + 1
            data[start_date_name] = data[start_date_name].astype(str) + "-01-01"
            data[end_date_name] = data[end_date_name].astype(str) + "-01-01"
        else:
            raise UserError(_("Invalid period."))

        # Check for the last month -- last day is today
        is_today_in_current_month = pd.DataFrame()
        is_today_in_current_month["bool"] = data[start_date_name].lt(today) & data[
            end_date_name
        ].gt(today)
        index_in_df = is_today_in_current_month[
            is_today_in_current_month["bool"]
        ].index.values
        if index_in_df:
            data[end_date_name].iloc[index_in_df[0]] = today

        business_days = data.apply(
            lambda row: np.busday_count(row[start_date_name], row[end_date_name]),
            axis=1,
        )
        data.insert(4, "Business days", business_days)

    def _generate_excel_export(self, data_by_day, data_by_month, data_by_year):

        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")

        data_by_month["Month"] = pd.to_datetime(
            data_by_month["Month"], errors="raise", format="%Y-%m-%d"
        )
        data_by_month["Month"] = data_by_month["Month"].dt.strftime("%m-%Y")

        cols = [
            "Month",
            "Turnover (stock moves)",
            "Turnover (prev. Month)",
            "Mensual grow",
            "Mean daily turnover",
            "Credit notes (stock moves)",
            "Turnover (accounting)",
            "Business days",
            "Business days (prev. Month)",
        ]
        data_by_month = data_by_month[cols]

        data_by_month.rename(
            columns={
                "Month": "Mois",
                "Turnover (stock moves)": u"CA année (stock moves)",
                "Turnover (prev. Month)": u"CA année-1 (stock moves)",
                "Mensual grow": "Taux de croissance mensuel (%)",
                "Mean daily turnover": "Moyenne CA",
                "Credit notes (stock moves)": u"Notes de crédit (stock moves)",
                "Turnover (accounting)": u"CA (comptabilité)",
                "Business days": u"Jours ouvrés",
                "Business days (prev. Month)": u"Jours ouvres année-1",
            },
            inplace=True,
        )

        data_by_year["Year"] = pd.to_datetime(
            data_by_year["Year"], errors="raise", format="%Y-%m-%d"
        )
        data_by_year["Year"] = data_by_year["Year"].dt.strftime("%Y")
        cols = [
            "Year",
            "Turnover (stock moves)",
            "Global grow",
            "Mean daily turnover",
            "Credit notes (stock moves)",
            "Turnover (accounting)",
            "Business days",
        ]
        data_by_year = data_by_year[cols]
        data_by_year.rename(
            columns={
                "Year": u"Année",
                "Turnover (stock moves)": u"CA année (stock moves)",
                "Global grow": "Taux de croissance global (%)",
                "Mean daily turnover": "Moyenne CA",
                "Credit notes (stock moves)": u"Notes de crédit (stock moves)",
                "Turnover (accounting)": u"CA (comptabilité)",
                "Business days": u"Jours ouvrés",
            },
            inplace=True,
        )

        data_by_month.to_excel(writer, sheet_name="rapportMois")
        data_by_year.to_excel(writer, sheet_name="rapportAn")
        # data_by_day.to_excel(writer, sheet_name="reportByDays")

        # Format excel to something nice
        workbook = writer.book
        worksheet1 = writer.sheets["rapportMois"]
        worksheet2 = writer.sheets["rapportAn"]
        # worksheet3 = writer.sheets["reportByDays"]
        formatSheet = workbook.add_format({"num_format": "0.00"})
        worksheet1.set_column("B:K", 30, formatSheet)
        worksheet2.set_column("B:H", 30, formatSheet)
        # worksheet3.set_column("B:E", 30, formatSheet)
        writer.save()

        excel_data = output.getvalue()
        return base64.b64encode(excel_data)

    @api.multi
    def get_export_data(self):
        this = self[0]

        # day by day Dataframe
        result = self._get_data_from_stock_moves(
            in_or_out_move="out_move", groupby_type="day"
        )
        debit_day_from_sm_df = self._sql_data_to_dataframe(
            result, ["date", "debit_from_sm"]
        )

        result2 = self._get_data_from_stock_moves(
            in_or_out_move="in_move", groupby_type="day"
        )
        credit_day_from_sm_df = self._sql_data_to_dataframe(
            result2, ["date", "credit_from_sm"]
        )

        credit_debit_day_from_sm_df = pd.merge(
            credit_day_from_sm_df, debit_day_from_sm_df, on="date"
        )

        credit_debit_day_from_sm_df["balance_from_sm"] = self._compute_CA_balance(
            credit_debit_day_from_sm_df["credit_from_sm"],
            credit_debit_day_from_sm_df["debit_from_sm"],
        )

        credit_debit_day_from_sm_df["date"] = pd.DatetimeIndex(
            credit_debit_day_from_sm_df["date"]
        )
        credit_debit_from_invoicing = self._get_data_from_invoicing(
            groupby_type="date:day"
        )
        credit_debit_from_invoicing_day_df = pd.DataFrame(credit_debit_from_invoicing)
        credit_debit_from_invoicing_day_df = credit_debit_from_invoicing_day_df.drop(
            ["__count", "__domain", "company_id"], axis=1
        ).rename(
            columns={
                "balance": "balance_from_invoicing",
                "credit": "credit_from_invoicing",
                "debit": "debit_from_invoicing",
                "date:day": "date",
            }
        )
        credit_debit_from_invoicing_day_df[
            "balance_from_invoicing"
        ] = -credit_debit_from_invoicing_day_df["balance_from_invoicing"]
        dates_formated = credit_debit_from_invoicing_day_df.apply(
            lambda row: datetime.strptime(row["date"], "%d %b %Y"), axis=1
        )
        credit_debit_from_invoicing_day_df["date"] = pd.DatetimeIndex(dates_formated)

        credit_debit_balance_day = pd.merge(
            credit_debit_from_invoicing_day_df,
            credit_debit_day_from_sm_df,
            on="date",
            how="outer",
        )
        # Keep only needed columns + reordering them
        credit_debit_balance_day.rename(
            columns={
                "balance_from_invoicing": "Turnover (accounting)",
                "date": "Day",
                "debit_from_sm": "Credit notes (stock moves)",
                "balance_from_sm": "Turnover (stock moves)",
            },
            inplace=True,
        )
        credit_debit_balance_day.drop(
            ["credit_from_invoicing", "debit_from_invoicing", "credit_from_sm"],
            axis=1,
            inplace=True,
        )
        cols = [
            "Day",
            "Turnover (stock moves)",
            "Credit notes (stock moves)",
            "Turnover (accounting)",
        ]
        credit_debit_balance_day = credit_debit_balance_day[cols]

        # Month by month Dataframe
        result = self._get_data_from_stock_moves(
            in_or_out_move="out_move", groupby_type="month"
        )
        debit_month_from_sm_df = self._sql_data_to_dataframe(
            result, ["date", "debit_from_sm"]
        )

        result2 = self._get_data_from_stock_moves(
            in_or_out_move="in_move", groupby_type="month"
        )
        credit_month_from_sm_df = self._sql_data_to_dataframe(
            result2, ["date", "credit_from_sm"]
        )

        credit_debit_from_sm_df = pd.merge(
            credit_month_from_sm_df, debit_month_from_sm_df, on="date"
        )

        credit_debit_from_sm_df["balance_from_sm"] = self._compute_CA_balance(
            credit_debit_from_sm_df["credit_from_sm"],
            credit_debit_from_sm_df["debit_from_sm"],
        )

        credit_debit_from_sm_df["date"] = pd.DatetimeIndex(
            credit_debit_from_sm_df["date"]
        )

        credit_debit_from_invoicing = self._get_data_from_invoicing(
            groupby_type="date:month"
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
        credit_debit_from_invoicing_df[
            "balance_from_invoicing"
        ] = -credit_debit_from_invoicing_df["balance_from_invoicing"]
        dates_formated = credit_debit_from_invoicing_df.apply(
            lambda row: datetime.strptime(row["date"], "%B %Y"), axis=1
        )
        credit_debit_from_invoicing_df["date"] = pd.DatetimeIndex(dates_formated)

        credit_debit_balance = pd.merge(
            credit_debit_from_invoicing_df,
            credit_debit_from_sm_df,
            on="date",
            how="outer",
        )
        # Keep only needed columns + reordering them
        credit_debit_balance.rename(
            columns={
                "balance_from_invoicing": "Turnover (accounting)",
                "date": "Month",
                "debit_from_sm": "Credit notes (stock moves)",
                "balance_from_sm": "Turnover (stock moves)",
            },
            inplace=True,
        )
        credit_debit_balance.drop(
            ["credit_from_invoicing", "debit_from_invoicing", "credit_from_sm"],
            axis=1,
            inplace=True,
        )

        cols = [
            "Month",
            "Turnover (stock moves)",
            "Credit notes (stock moves)",
            "Turnover (accounting)",
        ]
        credit_debit_balance = credit_debit_balance[cols]

        # compare = credit_debit_balance_day.groupby([credit_debit_balance_day["Day"].dt.year, credit_debit_balance_day["Day"].dt.month]
        # ).sum()
        today = datetime.today().date().strftime("%Y-%m-%d")
        self._count_business_days(credit_debit_balance, "Month", "Month+1", today)
        self._compute_mensual_grow(credit_debit_balance, today)

        credit_debit_balance.insert(
            5,
            "Mean daily turnover",
            credit_debit_balance["Turnover (stock moves)"]
            / credit_debit_balance["Business days"],
        )

        # Year by Year Dataframe
        credit_debit_from_sm_by_year = credit_debit_from_sm_df.groupby(
            credit_debit_from_sm_df["date"].dt.year
        ).sum()
        credit_debit_from_sm_by_year.reset_index(inplace=True)
        credit_debit_from_sm_by_year.rename(columns={"date": "Year"}, inplace=True)

        credit_debit_from_invoicing_by_year = credit_debit_from_invoicing_df.groupby(
            credit_debit_from_invoicing_df["date"].dt.year
        ).sum()
        credit_debit_from_invoicing_by_year.reset_index(inplace=True)
        credit_debit_from_invoicing_by_year.rename(
            columns={"date": "Year"}, inplace=True
        )

        credit_debit_balance_by_year = pd.merge(
            credit_debit_from_invoicing_by_year,
            credit_debit_from_sm_by_year,
            on="Year",
            how="outer",
        )

        credit_debit_balance_by_year.rename(
            columns={
                "balance_from_invoicing": "Turnover (accounting)",
                "debit_from_sm": "Credit notes (stock moves)",
                "balance_from_sm": "Turnover (stock moves)",
            },
            inplace=True,
        )
        credit_debit_balance_by_year.drop(
            ["credit_from_invoicing", "debit_from_invoicing", "credit_from_sm"],
            axis=1,
            inplace=True,
        )
        cols = [
            "Year",
            "Turnover (stock moves)",
            "Credit notes (stock moves)",
            "Turnover (accounting)",
        ]
        credit_debit_balance_by_year = credit_debit_balance_by_year[cols]

        # count business days
        self._count_business_days(credit_debit_balance_by_year, "Year", "Year+1", today)
        self._compute_global_grow(
            credit_debit_balance_by_year, credit_debit_balance, today
        )
        credit_debit_balance_by_year.drop(
            ["Year+1", "Turnover (prev. Year)", "Business days (prev. Year)"],
            axis=1,
            inplace=True,
        )
        credit_debit_balance.drop(["Month+1"], axis=1, inplace=True)
        credit_debit_balance_by_year.insert(
            5,
            "Mean daily turnover",
            credit_debit_balance_by_year["Turnover (stock moves)"]
            / credit_debit_balance_by_year["Business days"],
        )
        data = self._generate_excel_export(
            credit_debit_balance_day, credit_debit_balance, credit_debit_balance_by_year
        )

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
