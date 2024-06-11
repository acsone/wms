# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import index_exists

from odoo.addons.sale_margin_delivered.models import sale_margin


class SaleOrderLine(sale_margin.SaleOrderLine):
    def init(self):  # pylint: disable=missing-return
        super().init()
        if not index_exists(
            self._cr,
            "sale_order_line_negative_margin_delivered_percent_idx",
        ):
            self._cr.execute(
                """
                CREATE INDEX sale_order_line_negative_margin_delivered_percent_idx
                ON
                    sale_order_line (margin_delivered_percent) WHERE margin_delivered_percent < 0
                """
            )
        if not index_exists(
            self._cr,
            "sale_order_line_negative_margin_delivered_percent_no_promotion_idx",
        ):
            self._cr.execute(
                """
                CREATE INDEX sale_order_line_negative_margin_delivered_percent_no_promotion_idx
                ON
                    sale_order_line (margin_delivered_percent) WHERE margin_delivered_percent < 0 AND discount2 = 0
                """
            )
