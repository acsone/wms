# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import csv

from odoo.addons.report_csv.report.report_csv import ReportCSVAbstract


class AlcProductConsolidatedPriceCsvReport(ReportCSVAbstract):
    _name = "report.alc_product_consolidated_price_csv_report"
    _description = "Product consolidated price report"

    def generate_csv_report(self, file, data, partner):
        # Write header first
        file.writeheader()
        flattened_data = self._flattened_data(partner)
        for fdata in flattened_data:
            final_discount = self._get_final_discount(
                fdata.supplier_discount_discount_sale,
            )
            product = self.env["product.product"].browse(fdata.product_id)
            file.writerow(
                {
                    "REF": fdata.default_code,
                    "NAME": fdata.name,
                    "CNK": fdata.cnk_code or "",
                    "INDICATED_PRICE": fdata.indicated_price,
                    "TAXES": ", ".join(
                        product.taxes_id.filtered(
                            lambda t: t.amount_type == "percent"
                        ).mapped("description")
                    ),
                    "LIST_PRICE": fdata.gross_price,
                    "DISCOUNT": fdata.supplier_discount_discount_sale,
                    "NET_PRICE": fdata.gross_price * (1.0 - final_discount / 100.0),
                    "SUPPLIER": fdata.supplier_name,
                    "CATEGORY": fdata.categ,
                }
            )

    def csv_report_options(self):
        res = super().csv_report_options()
        res["fieldnames"].extend(
            [
                "REF",
                "NAME",
                "CNK",
                "INDICATED_PRICE",
                "TAXES",
                "LIST_PRICE",
                "DISCOUNT",
                "NET_PRICE",
                "SUPPLIER",
                "CATEGORY",
            ]
        )
        res["delimiter"] = ";"
        res["quoting"] = csv.QUOTE_ALL
        return res

    def _flattened_data(self, partner):
        return self.env["alc.product.flattened.data"]._get_partner_products_iterator(
            partner
        )

    @staticmethod
    def _get_final_discount(*discounts):
        discounts = [1 - (discount or 0.0) / 100 for discount in discounts]
        final_discount = 1
        for discount in discounts:
            final_discount *= discount
        return 100 - final_discount * 100
