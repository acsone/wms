# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.addons.product.models.product_product import ProductProduct as ProductBase


class ProductProduct(ProductBase):

    average_annual_sale = fields.Float(
        "Average annual sale",
        readonly=True,
        compute="_compute_average_sale",
        digits="Product Unit of Measure",
    )
    average_three_months_sale = fields.Float(
        "Average three months sale",
        readonly=True,
        compute="_compute_average_sale",
        digits="Product Unit of Measure",
        help="Average sale of the same three months period of the previous year.",
    )

    def _compute_average_sale(self):
        # Stop the method if self is empty.
        # Otherwise SQL query will fail (ids = [])
        if not self:
            return
        today = date.today()
        ids = tuple(self.ids)

        # Compute annual sale
        today_minus_one_year = today - relativedelta(years=1)
        annual_sale_per_products = self._average_sale(ids, today_minus_one_year, today)

        # Compute three months sale
        last_year_start = (today - relativedelta(years=1)).replace(day=1)
        last_year_end = last_year_start + relativedelta(months=3)
        three_months_sale_per_products = self._average_sale(
            ids, last_year_start, last_year_end
        )

        for product in self:
            annual_sale = annual_sale_per_products.get(product.id, 0)
            product.average_annual_sale = float(annual_sale) / 12 if annual_sale else 0

            three_months_sale = three_months_sale_per_products.get(product.id, 0)
            product.average_three_months_sale = (
                float(three_months_sale) / 3 if three_months_sale else 0
            )

    def _average_sale(self, ids, start_date, end_date):
        query = self._average_sale_query()
        self.env.cr.execute(query, (ids, start_date, end_date))
        return dict(self.env.cr.fetchall())

    def _average_sale_query(self):
        return """
            SELECT
              sol.product_id,
              sum(sol.product_uom_qty)
            FROM sale_order_line AS sol
              INNER JOIN sale_order so ON sol.order_id = so.id
            WHERE so.state IN ('sale', 'done')
              AND sol.product_id IN %s
              AND so.date_order >= %s
              AND so.date_order < %s
              AND so.state <> 'cancel'
            GROUP BY sol.product_id
        """
