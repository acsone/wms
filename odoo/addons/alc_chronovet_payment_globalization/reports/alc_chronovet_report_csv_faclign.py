# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import csv

from odoo import models


class AlcChronovetReportCsvFaclign(models.AbstractModel):
    _name = "report.alc_chronovet_report_csv_faclign"
    _description = "alc chronovet report csv faclign"
    _inherit = "report.report_csv.abstract"

    def _get_common_data(self, invoice, invoice_line):
        amount_tax = abs(invoice_line.price_total - invoice_line.price_subtotal)
        sign = -1 if invoice.move_type == "out_refund" else 1
        return {
            "CFACT": invoice.partner_id.ref or "",
            "CLIVR": invoice.partner_id.ref or "",
            "NOM": invoice.partner_id.name,
            "TYPE": invoice.move_type,
            "NFACT": invoice.name,
            "DATFAC": invoice.invoice_date,
            "CDART": invoice_line.product_id.default_code or "",
            "DESART": invoice_line.product_id.name,
            "PRIXUN": sign * invoice_line.price_unit,
            "PRIXREM": sign * invoice_line.price_subtotal / invoice_line.quantity,
            "QTFACT": invoice_line.quantity,
            "MONTHT": sign * invoice_line.price_subtotal,
            "GTIN14": invoice_line.product_id.barcode,
            "LABORATOIRE": invoice_line.product_id.supplier_id.name,
            "TVA": amount_tax,
            "CATEG": invoice_line.product_id.categ_id.parent_id.name
            if invoice_line.product_id.categ_id.parent_id
            else invoice_line.product_id.categ_id.name,
            "TOTALHT": sign * invoice_line.price_subtotal,
            "MONTTVA": sign * amount_tax,
            "TOTALTTC": sign * invoice_line.price_total,
        }

    def _add_sale_order_data(self, sale_order, common_data):
        sale_order_data = {
            "COMMANDE": sale_order.order_id.name,
            "NCOMM": sale_order.order_id.b2c_ref,
            "DATCDE": sale_order.date_order,
            "NLIVR": sale_order.order_id.picking_ids[0].name,
            "PROPRIETAIRE": sale_order.order_id.partner_id.name,
            "DATLIV": sale_order.order_id.picking_ids[0].date_done,
        }
        common_data.update(sale_order_data)
        return common_data

    def _add_data_for_no_so(self, common_data):
        no_so_data = {
            "COMMANDE": "",
            "NCOMM": "",
            "DATCDE": "",
            "NLIVR": "",
            "PROPRIETAIRE": "",
            "DATLIV": "",
        }
        common_data.update(no_so_data)
        return common_data

    def generate_csv_report(self, file, data, account_move):
        # Write header first
        file.writeheader()
        invoices = self._get_all_invoices(account_move)
        for invoice in invoices:
            for invoice_line in invoice.invoice_line_ids:
                common_data = self._get_common_data(invoice, invoice_line)
                if invoice_line.sale_line_ids:
                    for sale_order in invoice_line.sale_line_ids:
                        vals = self._add_sale_order_data(sale_order, common_data.copy())
                        file.writerow(vals)
                else:
                    vals = self._add_data_for_no_so(common_data.copy())
                    file.writerow(vals)

    def csv_report_options(self):
        res = super().csv_report_options()
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
        return account_move._get_reconciled_amls().move_id
