# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import csv

from odoo import models


class AlcProductConsolidatedPriceCsvReport(models.AbstractModel):
    _name = "report.alc_product_consolidated_price_csv_report"
    _inherit = "report.report_csv.abstract"

    def generate_csv_report(self, file, data, partner):
        # Write header first
        file.writeheader()
        consolidated_prices = self._consolidated_prices(partner)
        for cons_price in consolidated_prices:
            product = cons_price.product_id
            file.writerow(
                {
                    "REF": product.default_code,
                    "NAME": product.name,
                    "CNK": product.cnk_code or "",
                    "INDICATED_PRICE": product.indicated_price,
                    "TAXES": ", ".join(
                        product.taxes_id.filtered(
                            lambda t: t.amount_type == "percent"
                        ).mapped("description")
                    ),
                    "LIST_PRICE": product.list_price,
                    "DISCOUNT": cons_price.supplier_discount,
                    "NET_PRICE": cons_price.net_price,
                    "SUPPLIER": product.seller_ids[0].name.name
                    if product.seller_ids
                    else "",
                    "CATEGORY": product.categ_id.parent_id.display_name,
                }
            )

    def csv_report_options(self):
        res = super(AlcProductConsolidatedPriceCsvReport, self).csv_report_options()
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

    def _consolidated_prices(self, partner):
        return self.env["alc.product.partner.price"].search(
            [("partner_id", "=", partner.id)]
        )
