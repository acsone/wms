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
            for invoice_line in invoice.invoice_line_ids:
                for sale_order in invoice_line.sale_line_ids:
                    file.writerow(
                        {
                            "CFACT": invoice.partner_id.ref,
                            "CLIVR": invoice.partner_id.ref,
                            "NOM": invoice.partner_id.name,
                            "TYPE": invoice.type,
                            "COMMANDE": sale_order.order_id.name,
                            "NCOMM": sale_order.order_id.b2c_ref,
                            "DATCDE": sale_order.date_order,
                            "NLIVR": sale_order.order_id.picking_ids[0].name,
                            "NFACT": invoice.number,
                            "DATFAC": invoice.date_invoice,
                            "CDART": invoice_line.product_id.default_code,
                            "DESART": invoice_line.product_id.name,
                            "PRIXUN": invoice_line.price_unit,
                            "PRIXREM": invoice_line.price_subtotal
                            / invoice_line.quantity,
                            "QTFACT": invoice_line.quantity,
                            "MONTHT": invoice_line.price_subtotal,
                            "GTIN14": invoice_line.product_id.barcode,
                            "LABORATOIRE": invoice_line.product_id.supplier_id.name,
                            "TVA": invoice_line.invoice_line_tax_ids[0].amount,
                            "PROPRIETAIRE": sale_order.order_id.partner_id.name,
                            "CATEG": invoice_line.product_id.categ_id.parent_id.name
                            if invoice_line.product_id.categ_id.parent_id
                            else invoice_line.product_id.categ_id.name,
                            "TOTALHT": invoice_line.price_subtotal,
                            "MONTTVA": invoice_line.price_subtotal
                            * invoice_line.invoice_line_tax_ids[0].amount
                            / 100.0,
                            "TOTALTTC": invoice_line.price_subtotal
                            * (1 + invoice_line.invoice_line_tax_ids[0].amount / 100.0),
                            "DATLIV": sale_order.order_id.picking_ids[0].date_done,
                        }
                    )

    def csv_report_options(self):
        res = super(AlcChronovetReportCsvFaclign, self).csv_report_options()
        res["fieldnames"].extend(
            [
                "CFACT",
                "CLIVR",
                "NOM",
                "TYPE",
                "COMMANDE",
                "NCOMM",
                "DATCDE",
                "NLIVR",
                "NFACT",
                "DATFAC",
                "CDART",
                "DESART",
                "PRIXUN",
                "PRIXREM",
                "QTFACT",
                "MONTHT",
                "GTIN14",
                "LABORATOIRE",
                "CLASSE",
                "TVA",
                "PROPRIETAIRE",
                "CATEG",
                "TOTALHT",
                "MONTTVA",
                "TOTALTTC",
                "DATLIV",
            ]
        )
        res["delimiter"] = ";"
        res["quoting"] = csv.QUOTE_ALL
        return res

    def _get_all_invoices(self, account_move):
        return [line.invoice_id for line in account_move.line_ids if line.invoice_id]
