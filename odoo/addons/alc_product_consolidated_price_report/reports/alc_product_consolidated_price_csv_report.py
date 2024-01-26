# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import csv

from odoo import tools

from odoo.addons.report_csv.report.report_csv import ReportCSVAbstract


class AlcProductConsolidatedPriceCsvReport(ReportCSVAbstract):
    _name = "report.alc_product_consolidated_price_csv_report"
    _description = "Product consolidated price report"

    def generate_csv_report(self, file, data, partner):
        # Write header first
        file.writeheader()
        flattened_data = self._flattened_data(partner)
        for fdata in flattened_data:
            product = self.env["product.product"].browse(fdata.product_id)
            # get the list of keys to use to retrieve the alcyon discounts from
            # the cache allowed to the partner
            discount_keys = partner.discount_pricelist_ids.mapped("discount_role_name")
            # get the resolved discount from the cache )
            discount = (
                product._resolve_discount_cache_get(fdata.price_cache, discount_keys)
                or {}
            )
            alcyon_discount = discount.get("discount", 0)
            # the final discount is the multiplication of the supplier discount
            # and the alcyon discount
            final_discount = self._get_final_discount(
                fdata.supplier_discount_discount_sale, alcyon_discount
            )
            # the net price includes the supplier discount and the alcyon discount
            net_price = fdata.gross_price * (1.0 - final_discount / 100.0)
            net_price = tools.float_round(net_price, precision_rounding=0.01)
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
                    # the gross price is the price without any discount applied
                    # to the partner. It's based on the pricelist of the partner
                    "LIST_PRICE": fdata.gross_price,
                    # the supplier discount is the discount offered by the supplier
                    "DISCOUNT": fdata.supplier_discount_discount_sale,
                    # the list price includes the discount offered by the supplier
                    # and the discount offered by alcyon
                    "NET_PRICE": net_price,
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
