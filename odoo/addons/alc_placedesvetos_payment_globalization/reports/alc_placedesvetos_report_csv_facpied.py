# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import csv

from odoo import models


class AlcPlaceDesVetosReportCsvFacpied(models.AbstractModel):
    _name = "report.alc_placedesvetos_report_csv_facpied"
    _inherit = "report.report_csv.abstract"

    def generate_csv_report(self, file, data, account_move):
        # Write header first
        file.writeheader()
        invoices = self._get_all_invoices(account_move)
        for invoice in invoices:
            file.writerow(
                {
                    "CFACT": invoice.partner_id.ref,
                    "NOM": invoice.partner_id.name,
                    "TYPE": invoice.type,
                    "NFACT": invoice.number,
                    "DATEFACT": invoice.date_invoice,
                    "TVA": invoice.tax_line_ids[0].tax_id.amount,
                    "MONTHT": invoice.amount_untaxed,
                    "ESCOMPTE": 0,
                    "TOTALHT": invoice.amount_untaxed,
                    "MONTTVA": invoice.amount_tax,
                    "TOTALTTC": invoice.amount_total,
                }
            )

    def csv_report_options(self):
        res = super(AlcPlaceDesVetosReportCsvFacpied, self).csv_report_options()
        res["fieldnames"].extend(
            [
                "CFACT",
                "NOM",
                "TYPE",
                "NFACT",
                "DATEFACT",
                "TVA",
                "MONTHT",
                "ESCOMPTE",
                "TOTALHT",
                "MONTTVA",
                "TOTALTTC",
            ]
        )
        res["delimiter"] = ";"
        res["quoting"] = csv.QUOTE_ALL
        return res

    def _get_all_invoices(self, account_move):
        return [line.invoice_id for line in account_move.line_ids if line.invoice_id]
