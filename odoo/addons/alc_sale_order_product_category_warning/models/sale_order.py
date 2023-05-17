# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.sale.models.sale_order import SaleOrder as SaleOrderBase


class SaleOrder(SaleOrderBase):
    def _get_order_lines_to_report_separated_by_warnings(self):
        lines = self._get_order_lines_to_report()
        categories = lines.mapped("product_id.categ_id").filtered("warning_info")
        pharmacy_cat = self.env.ref("alc_product_category_data.product_categ_humain")
        pharmacy_warning = _("Article transferred to dispensing pharmacy: {}")
        # Group the lines by categories (with warning)
        all_lines_warning = []
        for category in categories:
            lines_warning = lines.filtered(
                lambda r, categ=category: r.product_id.categ_id.id == categ.id
            )
            additional_warning = ""
            if category == pharmacy_cat:
                additional_warning = pharmacy_warning.format(
                    self.partner_id.pharmacist_id.name or ""
                )
            all_lines_warning.append(
                {
                    "warning": category.warning_info,
                    "lines": lines_warning.sorted(),
                    "additional_info": additional_warning,
                }
            )
            lines -= lines_warning
        return {
            "lines_without_warning": lines,
            "lines_with_warning": all_lines_warning,
        }
