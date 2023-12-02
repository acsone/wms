# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tools import index_exists

from odoo.addons.sale.models.sale_order_line import SaleOrderLine as SaleOrderLineBase


class SaleOrderLine(SaleOrderLineBase):
    def init(self):  # pylint: disable=missing-return
        """
        This index improves the overall performance of picking validation.

        A flush_all in _update_reserved_quantity makes the computed fields recomputed
        with each stock.move action_done.
        The qty_invoiced in the sale.order.line model depends on stock.move qty_done
        and uses sale_order_line_invoice_rel to get invoice_lines.
        """
        super().init()
        if not index_exists(
            self._cr, "sale_order_line_invoice_rel_order_line_id_manidx"
        ):
            self._cr.execute(
                """
                CREATE INDEX sale_order_line_invoice_rel_order_line_id_manidx
                ON
                    sale_order_line_invoice_rel (order_line_id)
                """
            )
