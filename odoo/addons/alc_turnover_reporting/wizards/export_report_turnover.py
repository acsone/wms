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
                    date_trunc(%(groupby_type)s, sm.date) AS date,
                    SUM((sol.price_subtotal/sol.product_uom_qty) * sm.product_qty) AS debit_from_sm,
                    SUM(sm.price_unit * sm.product_qty) AS pp200_debit_from_sm FROM stock_move sm
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
                    date_trunc(%(groupby_type)s, sm.date) AS date,
                    SUM((sol.price_subtotal/sol.product_uom_qty) * sm.product_qty) AS credit_from_sm,
                    SUM(sm.price_unit *sm.product_qty) AS pp200_credit_from_sm FROM stock_move sm
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

    def _get_data_for_margin_from_invoicing(self):

        return (
            self.env["account.move.line"]
            .with_context(lang="en_US")
            .read_group(
                [
                    (
                        "account_id.tag_ids",
                        "=",
                        self.env.ref("__import__.account_account_tag_alcyn_pp-200").id,
                    )
                ],
                ["debit", "credit", "balance", "date", "company_id"],
                ["date:month", "company_id"],
                lazy=False,
            )
        )

    def _compute_CA_balance(self, credit, debit):
        return -(debit - credit)

    def _compute_mensual_grow(self, data, today):

        data.insert(
            2, "Turnover (prev. Month)", data["Turnover (stock moves)"].shift(12)
        )
        data.insert(6, "Business days (prev. Month)", data["Business days"].shift(12))

        data["Mensual grow"] = (
            data["Turnover (stock moves)"] - data["Turnover (prev. Month)"]
        ) / data["Turnover (prev. Month)"]
        data.loc[~np.isfinite(data["Mensual grow"]), "Mensual grow"] = np.nan

        # For unfinished month, specific treatment
        if data["Month+1"].iloc[-1].split("-")[1] == today.split("-")[1]:
            # grow = (CA_current_month - (CA_same_month_previous_year/business_days_month_prev_year)*business_days_current_month) /
            #           ((CA_same_month_previous_year/business_days_month_prev_year)*business_days_current_month)
            data["Mensual grow"].iloc[-1] = (
                data["Turnover (stock moves)"].iloc[-1]
                - (
                    data["Turnover (prev. Month)"].iloc[-1]
                    / data["Business days (prev. Month)"].iloc[-1]
                )
                * data["Business days"].iloc[-1]
            ) / (
                (
                    data["Turnover (prev. Month)"].iloc[-1]
                    / data["Business days (prev. Month)"].iloc[-1]
                )
                * data["Business days"].iloc[-1]
            )

    def _compute_global_grow(self, data_by_years, data_by_months, today):
        data_by_years["Turnover (prev. Year)"] = (
            data_by_years["Turnover (stock moves)"].shift(1).fillna(0)
        )
        data_by_years["Business days (prev. Year)"] = (
            data_by_years["Business days"].shift(1).fillna(0)
        )

        data_by_years["Global grow"] = (
            data_by_years["Turnover (stock moves)"]
            - data_by_years["Turnover (prev. Year)"]
        ) / data_by_years["Turnover (prev. Year)"]
        data_by_years.loc[
            ~np.isfinite(data_by_years["Global grow"]), "Global grow"
        ] = np.nan
        if data_by_months["Month+1"].iloc[-1].split("-")[1] == today.split("-")[1]:

            # If unfinished month : get the info from the month in the previous year
            current_month = today.split("-")[1]
            last_year = int(today.split("-")[0]) - 1
            date_to_get = str(last_year) + "-" + current_month + "-01"
            same_month_last_year = pd.DataFrame()
            same_month_last_year["bool"] = data_by_months["Month"].eq(date_to_get)
            index = same_month_last_year[same_month_last_year["bool"]].index.values

            if index:
                start_year = str(last_year) + "-10-01"
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
                    data_by_years["Turnover (stock moves)"].iloc[-1] - correction_factor
                ) / correction_factor

    def _count_business_days(self, data, start_date_name, end_date_name, today):
        # count business days
        if start_date_name == "Month":
            data[end_date_name] = data[start_date_name].dt.date + relativedelta(
                months=1
            )
            data[end_date_name] = data[end_date_name].astype(str)
            data[start_date_name] = data[start_date_name].astype(str)
        elif start_date_name == "Year":
            data[end_date_name] = data[start_date_name]
            data[start_date_name] = data[start_date_name].astype(int) - 1
            data[start_date_name] = data[start_date_name].astype(str) + "-10-01"
            data[end_date_name] = data[end_date_name].astype(str) + "-09-30"
        else:
            raise UserError(_("Invalid period."))

        # Check for the last month -- last day is today
        is_today_in_current_month = pd.DataFrame()
        is_today_in_current_month["bool"] = data[start_date_name].le(today) & data[
            end_date_name
        ].ge(today)
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

        today = datetime.today().date().strftime("%Y-%m-%d")
        data_by_day["Day"] = pd.to_datetime(
            data_by_day["Day"], errors="raise", format="%Y-%m-%d"
        )
        current_month = int(today.split("-")[1])
        current_year = int(today.split("-")[0])
        data_by_day = data_by_day[
            (data_by_day["Day"].dt.month == current_month)
            & (data_by_day["Day"].dt.year == current_year)
        ]

        data_by_day["Day"] = data_by_day["Day"].dt.strftime("%d-%m-%Y")

        cols = ["Day", "Turnover (stock moves)", "Credit notes (stock moves)"]
        data_by_day = data_by_day[cols]

        data_by_day.rename(
            columns={
                "Day": "Jour",
                "Turnover (stock moves)": u"CA jour \n(stock moves)",
                "Credit notes (stock moves)": u"Notes de crédit \n(stock moves)",
            },
            inplace=True,
        )

        data_by_month["Month"] = pd.to_datetime(
            data_by_month["Month"], errors="raise", format="%Y-%m-%d"
        )
        data_by_month["Year"] = data_by_month["Month"].dt.strftime("%Y")
        data_by_month[["Year"]] = data_by_month[["Year"]].mask(
            data_by_month.duplicated(["Year"])
        )
        data_by_month["Month"] = data_by_month["Month"].dt.strftime("%b")

        cols = [
            "Year",
            "Month",
            "Turnover (stock moves)",
            "Turnover (prev. Month)",
            "Mensual grow",
            "Margin (stock moves)",
            "Mean daily turnover",
            "Credit notes (stock moves)",
            "Turnover (accounting)",
            "Margin (accounting)",
            "Delta accounting - Stock moves",
            "Business days",
            "Business days (prev. Month)",
        ]
        data_by_month = data_by_month[cols]

        data_by_month.rename(
            columns={
                "Year": u"Année",
                "Month": "Mois",
                "Turnover (stock moves)": u"CA année \n (stock moves)",
                "Turnover (prev. Month)": u"CA année-1 \n (stock moves)",
                "Mensual grow": "Taux de croissance \nmensuel",
                "Mean daily turnover": "Moyenne CA",
                "Credit notes (stock moves)": u"Notes de crédit \n (stock moves)",
                "Turnover (accounting)": u"CA année \n (comptabilité)",
                "Delta accounting - Stock moves": u"Différence CA \n (stock moves - compta)",
                "Business days": u"Jours ouvrés",
                "Business days (prev. Month)": u"Jours ouvrés \nannée-1",
                "Margin (stock moves)": "Marge \n (stock moves)",
                "Margin (accounting)": u"Marge \n (comptabilité)",
            },
            inplace=True,
        )

        data_by_year["Year"] = pd.to_datetime(
            data_by_year["Year"], errors="raise", format="%Y-%m-%d"
        )

        data_by_year = data_by_year[
            (data_by_year["Year"].dt.year == current_year)
            | (data_by_year["Year"].dt.year == current_year - 1)
        ]
        data_by_year["Year"] = data_by_year["Year"].dt.strftime("%Y")
        cols = [
            "Year",
            "Turnover (stock moves)",
            "Global grow",
            "Mean daily turnover",
            "Credit notes (stock moves)",
            "Turnover (accounting)",
            "Delta accounting - Stock moves",
            "Business days",
        ]
        data_by_year = data_by_year[cols]
        data_by_year.rename(
            columns={
                "Year": u"Année",
                "Turnover (stock moves)": u"CA année \n (stock moves)",
                "Global grow": "Taux de croissance \n global",
                "Mean daily turnover": "Moyenne CA",
                "Credit notes (stock moves)": u"Notes de crédit \n (stock moves)",
                "Turnover (accounting)": u"CA année \n (comptabilité)",
                "Delta accounting - Stock moves": u"Différence CA \n (stock moves - compta)",
                "Business days": u"Jours ouvrés",
            },
            inplace=True,
        )
        data_by_month.reset_index(drop=True, inplace=True)
        data_by_month["Taux de croissance \nmensuel"].fillna(0, inplace=True)
        data_by_year["Taux de croissance \n global"].fillna(0, inplace=True)
        data_by_day.reset_index(drop=True, inplace=True)
        data_by_month.to_excel(
            writer, sheet_name="rapportMensuel", startrow=1, header=False
        )
        data_by_year.to_excel(
            writer, sheet_name="rapportAnnuel", startrow=1, header=False
        )
        data_by_day.to_excel(
            writer, sheet_name="rapportJournalier", startrow=1, header=False
        )

        # Format excel to something nice
        workbook = writer.book
        worksheet1 = writer.sheets["rapportMensuel"]
        worksheet2 = writer.sheets["rapportAnnuel"]
        worksheet3 = writer.sheets["rapportJournalier"]
        formatSheet = workbook.add_format({"num_format": "#.##0"})

        worksheet1.set_column("B:C", 10, formatSheet)
        worksheet1.set_column("D:E", 20, formatSheet)
        worksheet1.set_column("H:J", 20, formatSheet)
        worksheet1.set_column("M:N", 15, formatSheet)

        worksheet2.set_column("B:B", 10, formatSheet)
        worksheet2.set_column("C:C", 20, formatSheet)
        worksheet2.set_column("E:G", 20, formatSheet)
        worksheet2.set_column("I:I", 12, formatSheet)

        worksheet3.set_column("B:B", 10, formatSheet)
        worksheet3.set_column("C:D", 20, formatSheet)

        # Add a header format.
        header_format = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True, "text_wrap": True}
        )

        worksheet1.set_row(0, 45)
        # Write the column headers with the defined format.
        for col_num, value in enumerate(data_by_month.columns.values):
            worksheet1.write(0, col_num + 1, value, header_format)

        worksheet2.set_row(0, 45)
        # Write the column headers with the defined format.
        for col_num, value in enumerate(data_by_year.columns.values):
            worksheet2.write(0, col_num + 1, value, header_format)

        worksheet3.set_row(0, 45)
        # Write the column headers with the defined format.
        for col_num, value in enumerate(data_by_day.columns.values):
            worksheet3.write(0, col_num + 1, value, header_format)

        red_format = workbook.add_format({"font_color": "#f50710"})
        worksheet1.conditional_format(
            "F2:F{}".format(len(data_by_month) + 1),
            {"type": "cell", "criteria": "<", "value": 0, "format": red_format},
        )

        red_format = workbook.add_format({"font_color": "#f50710"})
        worksheet2.conditional_format(
            "D2:D{}".format(len(data_by_year) + 1),
            {"type": "cell", "criteria": "<", "value": 0, "format": red_format},
        )

        percentFormat1 = workbook.add_format({"num_format": "0.0%"})
        worksheet1.set_column("F:F", 20, percentFormat1)
        worksheet1.set_column("G:G", 15, percentFormat1)
        worksheet1.set_column("K:K", 15, percentFormat1)
        worksheet1.set_column("L:L", 20, percentFormat1)

        worksheet2.set_column("D:D", 20, percentFormat1)
        worksheet2.set_column("H:H", 20, percentFormat1)

        len_data_charts = len(data_by_month)
        len_serie_2 = len(data_by_month[12:])
        chart = workbook.add_chart({"type": "column"})

        today = datetime.today().date().strftime("%Y-%m-%d")
        current_year = today.split("-")[0]
        if today <= current_year + "-09-30":
            previous_year = int(current_year) - 1
            previous_previous_year = int(current_year) - 2
            current_exercice = str(previous_year) + "-" + str(current_year)
            prev_exercice = str(previous_previous_year) + "-" + str(previous_year)
        else:
            next_year = int(current_year) + 1
            previous_year = int(current_year) - 1
            prev_exercice = str(previous_year) + "-" + str(current_year)
            current_exercice = str(current_year) + "-" + str(next_year)

        # Configure the first series.
        chart.add_series(
            {
                "name": u"CA Exercice {}".format(prev_exercice),
                "categories": "=rapportMensuel!C$2:$C$13",
                "values": "=rapportMensuel!$D$2:$D$13",
            }
        )

        # Configure a second series. Note use of alternative syntax to define ranges.
        chart.add_series(
            {
                "name": u"CA Exercice {}".format(current_exercice),
                "categories": "=rapportMensuel!$C$14:$C${}".format(13 + len_serie_2),
                "values": "=rapportMensuel!$D$14:$D${}".format(13 + len_serie_2),
            }
        )

        # Add a chart title and some axis labels.
        chart.set_title({"name": "CA annuel"})
        chart.set_y_axis({"name": u"CA (€)"})
        chart.set_x_axis(
            {
                "name": "Mois",
                "major_gridlines": {
                    "visible": True,
                    "line": {"width": 1.25, "dash_type": "dash"},
                },
            }
        )
        # Set an Excel chart style.
        chart.set_style(11)
        chart.set_size({"x_scale": 1.5, "y_scale": 2})
        # Insert the chart into the worksheet (with an offset).
        worksheet1.insert_chart("C{}".format(len_data_charts + 4), chart)

        writer.save()

        excel_data = output.getvalue()
        return base64.b64encode(excel_data)

    @api.multi
    def get_export_data(self):
        this = self[0]

        today = datetime.today().date().strftime("%Y-%m-%d")
        # day by day Dataframe
        result = self._get_data_from_stock_moves(
            in_or_out_move="out_move", groupby_type="day"
        )
        debit_day_from_sm_df = self._sql_data_to_dataframe(
            result, ["date", "debit_from_sm", "pp200_debit_from_sm"]
        )

        result2 = self._get_data_from_stock_moves(
            in_or_out_move="in_move", groupby_type="day"
        )
        credit_day_from_sm_df = self._sql_data_to_dataframe(
            result2, ["date", "credit_from_sm", "pp200_credit_from_sm"]
        )

        credit_debit_day_from_sm_df = pd.merge(
            credit_day_from_sm_df, debit_day_from_sm_df, on="date", how="outer"
        )
        credit_debit_day_from_sm_df.fillna(0, inplace=True)
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

        credit_debit_balance_day.sort_values(by=["date"], inplace=True)
        # Keep only needed columns + reordering them
        credit_debit_balance_day.rename(
            columns={
                "date": "Day",
                "debit_from_sm": "Credit notes (stock moves)",
                "balance_from_sm": "Turnover (stock moves)",
            },
            inplace=True,
        )
        credit_debit_balance_day.drop(
            [
                "credit_from_invoicing",
                "debit_from_invoicing",
                "credit_from_sm",
                "pp200_debit_from_sm",
                "pp200_credit_from_sm",
                "balance_from_invoicing",
            ],
            axis=1,
            inplace=True,
        )
        cols = ["Day", "Turnover (stock moves)", "Credit notes (stock moves)"]
        credit_debit_balance_day = credit_debit_balance_day[cols]

        credit_debit_balance_day.reset_index(drop=True, inplace=True)

        # Month by month Dataframe
        result = self._get_data_from_stock_moves(
            in_or_out_move="out_move", groupby_type="month"
        )
        debit_month_from_sm_df = self._sql_data_to_dataframe(
            result, ["date", "debit_from_sm", "pp200_debit_from_sm"]
        )

        result2 = self._get_data_from_stock_moves(
            in_or_out_move="in_move", groupby_type="month"
        )
        credit_month_from_sm_df = self._sql_data_to_dataframe(
            result2, ["date", "credit_from_sm", "pp200_credit_from_sm"]
        )

        credit_debit_from_sm_df = pd.merge(
            credit_month_from_sm_df, debit_month_from_sm_df, on="date", how="outer"
        )
        credit_debit_from_sm_df.fillna(0, inplace=True)

        credit_debit_from_sm_df["balance_from_sm"] = self._compute_CA_balance(
            credit_debit_from_sm_df["credit_from_sm"],
            credit_debit_from_sm_df["debit_from_sm"],
        )

        credit_debit_from_sm_df["pp200_balance_from_sm"] = self._compute_CA_balance(
            credit_debit_from_sm_df["pp200_credit_from_sm"],
            credit_debit_from_sm_df["pp200_debit_from_sm"],
        )
        credit_debit_from_sm_df["date"] = pd.DatetimeIndex(
            credit_debit_from_sm_df["date"]
        )

        credit_debit_from_sm_df["margin_from_sm"] = (
            credit_debit_from_sm_df["balance_from_sm"]
            - credit_debit_from_sm_df["pp200_balance_from_sm"]
        ) / credit_debit_from_sm_df["balance_from_sm"]
        credit_debit_from_invoicing = self._get_data_from_invoicing(
            groupby_type="date:month"
        )
        pp200_from_invoicing = self._get_data_for_margin_from_invoicing()
        credit_debit_from_invoicing_df = pd.DataFrame(credit_debit_from_invoicing)
        pp200_from_invoicing_df = pd.DataFrame(pp200_from_invoicing)
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

        pp200_from_invoicing_df = pp200_from_invoicing_df.drop(
            ["__count", "__domain", "company_id", "credit", "debit"], axis=1
        ).rename(
            columns={"balance": "pp200_balance_from_invoicing", "date:month": "date"}
        )

        credit_debit_from_invoicing_df[
            "balance_from_invoicing"
        ] = -credit_debit_from_invoicing_df["balance_from_invoicing"]
        dates_formated = credit_debit_from_invoicing_df.apply(
            lambda row: datetime.strptime(row["date"], "%B %Y"), axis=1
        )
        credit_debit_from_invoicing_df["date"] = pd.DatetimeIndex(dates_formated)

        dates_formated = pp200_from_invoicing_df.apply(
            lambda row: datetime.strptime(row["date"], "%B %Y"), axis=1
        )
        pp200_from_invoicing_df["date"] = pd.DatetimeIndex(dates_formated)
        temporary_df = pd.merge(
            pp200_from_invoicing_df,
            credit_debit_from_invoicing_df,
            on="date",
            how="outer",
        )
        credit_debit_balance = pd.merge(
            temporary_df, credit_debit_from_sm_df, on="date", how="outer"
        )
        credit_debit_balance.sort_values(by=["date"], inplace=True)
        credit_debit_balance.fillna(0, inplace=True)
        credit_debit_balance["margin_from_invoicing"] = (
            credit_debit_balance["balance_from_invoicing"]
            - credit_debit_balance["pp200_balance_from_invoicing"]
        ) / credit_debit_balance["balance_from_invoicing"]

        # Keep only needed columns + reordering them
        credit_debit_balance.rename(
            columns={
                "balance_from_invoicing": "Turnover (accounting)",
                "date": "Month",
                "debit_from_sm": "Credit notes (stock moves)",
                "balance_from_sm": "Turnover (stock moves)",
                "margin_from_invoicing": "Margin (accounting)",
                "margin_from_sm": "Margin (stock moves)",
            },
            inplace=True,
        )

        credit_debit_balance["Delta accounting - Stock moves"] = (
            credit_debit_balance["Turnover (stock moves)"]
            - credit_debit_balance["Turnover (accounting)"]
        ) / credit_debit_balance["Turnover (accounting)"]

        credit_debit_balance.reset_index(drop=True, inplace=True)
        credit_debit_balance.drop(
            [
                "credit_from_invoicing",
                "debit_from_invoicing",
                "credit_from_sm",
                "pp200_balance_from_invoicing",
                "pp200_credit_from_sm",
                "pp200_debit_from_sm",
            ],
            axis=1,
            inplace=True,
        )

        cols = [
            "Month",
            "Turnover (stock moves)",
            "Credit notes (stock moves)",
            "Turnover (accounting)",
            "Delta accounting - Stock moves",
            "Margin (stock moves)",
            "Margin (accounting)",
        ]
        credit_debit_balance = credit_debit_balance[cols]

        self._count_business_days(credit_debit_balance, "Month", "Month+1", today)
        self._compute_mensual_grow(credit_debit_balance, today)

        credit_debit_balance.insert(
            5,
            "Mean daily turnover",
            credit_debit_balance["Turnover (stock moves)"]
            / credit_debit_balance["Business days"],
        )

        # Year by Year Dataframe

        credit_debit_balance_month = credit_debit_balance.copy()
        credit_debit_balance_month.drop(
            [
                "Mean daily turnover",
                "Business days",
                "Turnover (prev. Month)",
                "Mensual grow",
                "Business days (prev. Month)",
                "Month+1",
                "Delta accounting - Stock moves",
            ],
            inplace=True,
            axis=1,
        )

        current_year = today.split("-")[0]
        two_years_ago = int(today.split("-")[0]) - 2
        date_to_get = str(two_years_ago) + "-10-01"
        october_two_years_ago = pd.DataFrame()
        october_two_years_ago["bool"] = credit_debit_balance_month["Month"].eq(
            date_to_get
        )
        index_two_ago = (
            october_two_years_ago[october_two_years_ago["bool"]].index.values
            if october_two_years_ago[october_two_years_ago["bool"]].index.values
            else [0]
        )

        last_year = int(today.split("-")[0]) - 1
        date_to_get = str(last_year) + "-10-01"
        october_last_year = pd.DataFrame()
        october_last_year["bool"] = credit_debit_balance_month["Month"].eq(date_to_get)
        index_last_year = (
            october_last_year[october_last_year["bool"]].index.values
            if october_last_year[october_last_year["bool"]].index.values
            else [0]
        )

        this_year = today.split("-")[0]
        date_to_get = this_year + "-10-01"
        october_this_year = pd.DataFrame()
        october_this_year["bool"] = credit_debit_balance_month["Month"].eq(date_to_get)
        index_this_year = october_this_year[october_this_year["bool"]].index.values

        credit_debit_2_years = credit_debit_balance_month.iloc[
            index_two_ago[0] : index_last_year[0]
        ]
        list_2_years = [
            credit_debit_2_years["Month"].iloc[-1].split("-")[0],
            credit_debit_2_years["Turnover (stock moves)"].sum(),
            credit_debit_2_years["Credit notes (stock moves)"].sum(),
            credit_debit_2_years["Turnover (accounting)"].sum(),
        ]

        if today <= current_year + "-09-30":
            # need to go to n-3 to compute global grow
            three_years_ago = int(today.split("-")[0]) - 3
            date_to_get = str(three_years_ago) + "-10-01"
            october_three_years_ago = pd.DataFrame()
            october_three_years_ago["bool"] = credit_debit_balance_month["Month"].eq(
                date_to_get
            )
            index_three_ago = (
                october_three_years_ago[october_three_years_ago["bool"]].index.values
                if october_three_years_ago[october_three_years_ago["bool"]].index.values
                else [0]
            )
            credit_debit_3_years = credit_debit_balance_month.iloc[
                index_three_ago[0] : index_two_ago[0]
            ]
            list_3_years = [
                credit_debit_3_years["Month"].iloc[-1].split("-")[0],
                credit_debit_3_years["Turnover (stock moves)"].sum(),
                credit_debit_3_years["Credit notes (stock moves)"].sum(),
                credit_debit_3_years["Turnover (accounting)"].sum(),
            ]

            credit_debit_last_year = credit_debit_balance_month.iloc[
                index_last_year[0] :
            ]
            list_last_year = [
                str(int(credit_debit_last_year["Month"].iloc[-1].split("-")[0]) + 1),
                credit_debit_last_year["Turnover (stock moves)"].sum(),
                credit_debit_last_year["Credit notes (stock moves)"].sum(),
                credit_debit_last_year["Turnover (accounting)"].sum(),
            ]

            by_year_grouping = [list_3_years, list_2_years, list_last_year]

            credit_debit_balance = credit_debit_balance.iloc[index_two_ago[0] :]
        else:
            credit_debit_last_year = credit_debit_balance_month.iloc[
                index_last_year[0] : index_this_year[0]
            ]
            list_last_year = [
                credit_debit_last_year["Month"].iloc[-1].split("-")[0],
                credit_debit_last_year["Turnover (stock moves)"].sum(),
                credit_debit_last_year["Credit notes (stock moves)"].sum(),
                credit_debit_last_year["Turnover (accounting)"].sum(),
            ]

            credit_debit_this_year = credit_debit_balance_month.iloc[
                index_this_year[0] :
            ]

            list_this_year = [
                str(int(credit_debit_this_year["Month"].iloc[-1].split("-")[0]) + 1),
                credit_debit_this_year["Turnover (stock moves)"].sum(),
                credit_debit_this_year["Credit notes (stock moves)"].sum(),
                credit_debit_this_year["Turnover (accounting)"].sum(),
            ]

            by_year_grouping = [list_2_years, list_last_year, list_this_year]
            credit_debit_balance = credit_debit_balance.iloc[index_last_year[0] :]

        cols = [
            "Year",
            "Turnover (stock moves)",
            "Credit notes (stock moves)",
            "Turnover (accounting)",
        ]
        credit_debit_balance_by_year = pd.DataFrame(data=by_year_grouping, columns=cols)
        credit_debit_balance_by_year["Delta accounting - Stock moves"] = (
            credit_debit_balance_by_year["Turnover (stock moves)"]
            - credit_debit_balance_by_year["Turnover (accounting)"]
        ) / credit_debit_balance_by_year["Turnover (accounting)"]

        years = credit_debit_balance_by_year["Year"]
        # count business days
        self._count_business_days(credit_debit_balance_by_year, "Year", "Year+1", today)
        self._compute_global_grow(
            credit_debit_balance_by_year, credit_debit_balance, today
        )
        credit_debit_balance_by_year["Year"] = years
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
