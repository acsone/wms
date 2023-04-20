# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime

from odoo import fields
from odoo.tools import float_compare, float_round

from odoo.addons.product.models.product_product import ProductProduct as ProductBase


class ProductProduct(ProductBase):

    advised_qty = fields.Integer(
        "Advised quantity", readonly=True, compute="_compute_advised_qty"
    )

    def _compute_advised_qty(self):
        """
        Compute an advised quantity.

        The advised quantity must be the same
        as the value computed by reordering rules
        :return:
        """
        orderpoints = self.mapped("orderpoint_ids")

        # Compute quantities to subtract
        if orderpoints:
            subtract_quantity = orderpoints._quantity_in_progress()
        else:
            subtract_quantity = {}

        for product in self:
            virtual_available = product.virtual_available
            orderpoint = product.orderpoint_ids and product.orderpoint_ids[0]

            # If there are some products in stock and if there are no
            # min/max (orderpoint), we don't need to compute a value
            # E.G: Stock = -4; min = 0 => -4 - 0 = -4 and -4 < 0 => compute
            # Stock: 5; min = 3 => 5 - 3 = 2 and 2 > 0 => no compute
            diff_qty = float_compare(
                virtual_available,
                orderpoint.product_min_qty,
                precision_rounding=product.uom_id.rounding,
            )
            if diff_qty > 0:
                product.advised_qty = False
                continue

            # Compute the qty to order
            # E.G: Stock = -4; min = 4; max = 10 => 10 - (-4) = 14
            qty = (
                max(orderpoint.product_min_qty, orderpoint.product_max_qty)
                - virtual_available
            )

            # Check if we need to order this product by multiple
            # E.G: Qty to order: 14; multiple 5 => remainder = 4
            remainder = (
                qty % orderpoint.qty_multiple if orderpoint.qty_multiple > 0 else 0.0
            )

            # Check if the difference between the remainder qty is greater
            # or less than 50% of the multiple qty
            # E.G: Remainder = 4; Multiple = 5 => Diff = 4 - (5 / 2) = 1,5
            remainder_diff = float_compare(
                remainder,
                orderpoint.qty_multiple / 2.0,
                precision_rounding=orderpoint.product_uom.rounding,
            )

            # If the remainder is greater or equal than 50% of the qty multiple
            # => We complete the quantity with the qty multiple
            # E.G: Diff = 1,5; Qty = 14; Multiple = 5; Remainder = 4
            # 14 + (5 - 4) = 15
            if remainder_diff >= 0:
                qty += orderpoint.qty_multiple - remainder
            # The remainder is less than 50% of the qty multiple
            # => We remove the remainder in the quantity
            # E.G: Diff = -1,5; Qty = 11; Multiple = 5; Remainder = 1
            # 11 - 1 = 10
            elif remainder:
                qty -= remainder

            if (
                float_compare(
                    qty, 0.0, precision_rounding=orderpoint.product_uom.rounding
                )
                < 0
            ):
                continue

            if orderpoint and orderpoint.id in subtract_quantity:
                qty -= subtract_quantity[orderpoint.id]
            qty_rounded = float_round(
                qty, precision_rounding=orderpoint.product_uom.rounding
            )
            if qty_rounded > 0:
                product.advised_qty = qty_rounded
            else:
                product.advised_qty = False

    def get_lots(self):
        self.ensure_one()

        lots = self.env["stock.lot"].search(
            [("product_id", "=", self.id)],
            order="expiration_date",
        )

        return lots

    def get_promotions(self):
        self.ensure_one()

        sellers = self.seller_ids
        sellers_with_discount = sellers.filtered(
            lambda s: s.discount or s.ratio_promotional_product
        )
        sellers_with_discount.sorted(lambda seller: seller.date_start)

        return list(sellers_with_discount)

    def get_graph_values(self):
        """
        Return the number of sale by month on 1 year.

        january is always the first value and december is always the last value

        - If the month is in the past (eg: date today == 15 February 2018
        and the month is January), this method will take data in the current
        year

        - If the month is the current month (eg: date today == 15 February 2018
        and the month is February), this method will return two values.
        One value from the first day of month to last day of the current year
        (eg: 1 February 2018 to 14 February 2018) and from the current day to
        the end of the month of the last year (eg: 15 February 2017 to
        28 February 2017).

        - If the month is in the future (eg: date today == 15 February 2018
        and the month is July), this method will take data in the last year/

        :return: Return a dict of values
        """
        self.ensure_one()

        # Retrieve sales by year/month (eg: 2017-07)
        query = """
        SELECT
          to_char(so.date_order, 'YYYY-MM') AS year_month,
          sum(sol.product_uom_qty)
        FROM sale_order_line AS sol
          INNER JOIN sale_order so ON sol.order_id = so.id
        WHERE so.state IN ('sale', 'done')
          AND sol.product_id = %s
          AND so.date_order::DATE >= (NOW() - INTERVAL '1 year')::DATE
          AND so.date_order::DATE < NOW()::DATE
          AND so.state <> 'cancel'
        GROUP BY year_month
        ORDER BY year_month;
        """

        # Store values
        self.env.cr.execute(query, (self.id,))
        values = dict(self.env.cr.fetchall())

        # Loop on 12 months
        graph_values = []
        today = datetime.today()
        for month in range(1, 13):
            # If the current month is less than today
            # (take data in the current year)
            if month < today.month:
                label = f"{month}/{str(today.year)[2:]}"
                value = values.get(f"{today.year}-{month:02}", 0)
                month_values = [{"label": label, "value": value}]
            # If the current month is the same than today
            # (take data in the current year AND in the last year)
            elif month == today.month:
                # We don't take values in the current year if we are the first
                # day of month (there are no data for the current month)
                if today.day == 1:
                    label = f"{month}/{str(today.year - 1)[2:]}"
                    value = values.get(f"{today.year - 1}-{month}", 0)
                    month_values = [{"label": label, "value": value}]
                # Otherwise we take values in the current year and in the last
                # year
                else:
                    label_current_year = (
                        f"{today.day - 1}/{month}/{str(today.year)[2:]}"
                    )
                    value_current_year = values.get(f"{today.year}-{month}", 0)

                    label_last_year = f"{today.day}/{month}/{str(today.year - 1)[2:]}"
                    value_last_year = values.get(f"{today.year - 1}-{month}", 0)

                    month_values = [
                        {"label": label_current_year, "value": value_current_year},
                        {"label": label_last_year, "value": value_last_year},
                    ]
            # Otherwise we take values in the last year
            else:
                label = f"{month}/{str(today.year - 1)[2:]}"
                value = values.get(f"{today.year - 1}-{month}", 0)
                month_values = [{"label": label, "value": value}]

            graph_values += month_values

        result = graph_values

        return result
