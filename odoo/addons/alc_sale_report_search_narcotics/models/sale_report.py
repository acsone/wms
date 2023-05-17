# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.report.sale_report import SaleReport as SaleReportBase


class SaleReport(SaleReportBase):
    # This is a dummy field to add a search functionality
    # based on defined category. See search method.
    only_narcotic = fields.Boolean(
        store=False,
        readonly=True,
        search="_search_only_narcotic",
        string="Only narcotics",
    )

    def _search_only_narcotic(self, operator, value):
        # Use only in search view
        domain = []
        category_narcotic = self.env.ref(
            "alc_product_category_data.product_categ_medoc", raise_if_not_found=False
        )
        if category_narcotic:
            domain.append(("categ_id", "child_of", category_narcotic.ids))
        return domain
