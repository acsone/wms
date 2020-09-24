# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import csv

from odoo import models


class AlcChronovetReportCsvFaclign(models.AbstractModel):
    _name = "report.alc_chronovet_report_csv_faclign"
    _inherit = "report.report_csv.abstract"

    def generate_csv_report(self, file, data, account_move):
        # Write header first
        file.writeheader()
        invoices = self._get_all_invoices(account_move)
        for invoice in invoices:
            file.writerow(
                {
                    "CFACT": invoice.partner_id.ref,
                    "CLIVR": invoice.partner_id.ref,
                    "NOM": invoice.partner_id.name,
                    "REGROUP": "",
                    "TYPE": invoice.type,
                    "COMMANDE": invoice.purchase_id.id,
                    "NCOMM": "",
                    "DATCDE": invoice.purchase_id.date_order,
                    "NLIVR": "",
                    "NFACT": invoice.number,
                    "DATFACT": invoice.date_invoice,
                    "CDART": invoice.invoice_line_ids[0].product_id.code,
                    "DESART": invoice.invoice_line_ids[0].product_id.description,
                    "PRIXUN": "",
                    "PRIXREM": "",
                    "QTFACT": invoice.quantity,
                    "MONTHT": invoice.amount_untaxed,
                    "PDSBRUT": "",
                    "PDSNET": "",
                    "GTIN14": invoice.purchase_id.product_id.barcode,
                    "LABORATOIRE": "",
                    "CLASSE": "",
                    "ESCOMPTE": 0,
                    "TVA": invoice.tax_line_ids[0].tax_id.amount,
                    "PROMO": invoice.discount,
                    "PROPRIETAIRE": "",
                    "CLTHER": "",
                    "SCLTHER": "",
                    "SSCLTHER": "",
                    "CATEG": "",
                    "MONTESC": "",
                    "TOTALHT": invoice.amount_untaxed,
                    "MONTTVA": invoice.amount_tax,
                    "TOTALTTC": invoice.amount_total,
                    "DATLIV": "",
                    "CIP": "",
                    "PUCAT": "",
                }
            )

    def csv_report_options(self):
        res = super(AlcChronovetReportCsvFaclign, self).csv_report_options()
        res["fieldnames"].extend(
            [
                "CFACT",
                "CLIVR",
                "NOM",
                "REGROUP",
                "TYPE",
                "COMMANDE",
                "NCOMM",
                "DATCDE",
                "NLIVR",
                "NFACT",
                "DATFACT",
                "CDART",
                "DESART",
                "PRIXUN",
                "PRIXREM",
                "QTFACT",
                "MONTHT",
                "PDSBRUT",
                "PDSNET",
                "GTIN14",
                "LABORATOIRE",
                "CLASSE",
                "ESCOMPTE",
                "TVA",
                "PROMO",
                "PROPRIETAIRE",
                "CLTHER",
                "SCLTHER",
                "SSCLTHER",
                "CATEG",
                "MONTESC",
                "TOTALHT",
                "MONTTVA",
                "TOTALTTC",
                "DATLIV",
                "CIP",
                "PUCAT",
            ]
        )
        res["delimiter"] = ";"
        res["quoting"] = csv.QUOTE_ALL
        return res

    def _get_all_invoices(self, account_move):
        return [line.invoice_id for line in account_move.line_ids if line.invoice_id]
