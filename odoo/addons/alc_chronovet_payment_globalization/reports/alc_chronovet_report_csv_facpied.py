# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import csv

from odoo import models


class AlcChronovetReportCsvFacpied(models.AbstractModel):
    _name = "report.alc_chronovet_report_csv_facpied"
    _inherit = "report.report_csv.abstract"

    def generate_csv_report(self, writer, data, account_moves):
        writer.writeheader()
        invoices = self._get_all_invoives(account_moves)
        for invoice in invoices:
            writer.writerow(
                {
                    "CFACT": invoice.partner_id.ref,
                    "NOM": invoice.partner_id.name,
                    "TYPE": "",
                    "NFACT": "",
                    "DATEFACT": "",
                    "TVA": "",
                    "MONTHT": "",
                    "ESCOMPTE": "",
                    "TOTALHT": "",
                    "MONTTVA": "",
                    "TOTALTTC": "",
                }
            )

    def csv_report_options(self):
        res = super(AlcChronovetReportCsvFacpied, self).csv_report_options()
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

    def _get_all_invoices(self, account_moves):
        invoice_ids = []
        return invoice_ids
