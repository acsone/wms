# Copyright 2019 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.purchase.models.product import ProductProduct as Product


class ProductProduct(Product):

    product_last_in_date = fields.Datetime(
        "Last Purchasing Date", compute="_compute_product_last_in_date"
    )
    product_last_out_date = fields.Datetime(
        "Last Selling Date", compute="_compute_product_last_out_date"
    )

    def _compute_product_last_in_date(self):
        for_date = self._context.get("history_date", fields.Datetime.now())
        self._cr.execute(
            """
            SELECT DISTINCT ON (product_id)
                purchase_order_line.product_id,
                purchase_order.date_order
            FROM purchase_order_line
            LEFT JOIN purchase_order
                ON purchase_order_line.order_id=purchase_order.id
            WHERE price_unit > 0
              AND purchase_order.date_order <= %s
              AND purchase_order_line.state in ('purchase', 'done')
              AND purchase_order_line.product_id in %s
            ORDER BY
                purchase_order_line.product_id,
                purchase_order.date_order desc
            """,
            (for_date, tuple(self.ids)),
        )
        dates_by_product = dict(self._cr.fetchall())
        for rec in self:
            rec.product_last_in_date = dates_by_product.get(rec.id, False)

    def _compute_product_last_out_date(self):
        for_date = self._context.get("history_date", fields.Datetime.now())
        self._cr.execute(
            """
            SELECT DISTINCT ON (product_id)
                sale_order_line.product_id,
                sale_order.date_order
            FROM sale_order_line
            LEFT JOIN sale_order
                ON sale_order_line.order_id=sale_order.id
            WHERE price_unit > 0
              AND date_order <= %s
              AND sale_order_line.state != 'cancel'
              AND sale_order_line.product_id in %s
            ORDER BY
                sale_order_line.product_id,
                sale_order.date_order desc
            """,
            (for_date, tuple(self.ids)),
        )
        dates_by_product = dict(self._cr.fetchall())
        for rec in self:
            rec.product_last_out_date = dates_by_product.get(rec.id, False)
