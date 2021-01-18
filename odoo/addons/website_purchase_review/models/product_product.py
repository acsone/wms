# -*- coding: utf-8 -*-
# © 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.tools import float_compare, float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    advised_qty = fields.Integer(
        "Advised quantity", readonly=True, compute="_compute_advised_qty"
    )
    average_annual_consumption = fields.Float(
        "Average annual consumption",
        readonly=True,
        compute="_compute_average_consumption",
    )
    average_three_months_consumption = fields.Float(
        "Average three months consumption",
        readonly=True,
        compute="_compute_average_consumption",
    )

    @api.multi
    def _compute_advised_qty(self):
        """
        Compute an advised quantity. The advised quantity must be the same
        than the value computed by reordering rules
        :return:
        """
        orderpoints = self.mapped("orderpoint_ids")

        # Compute quantities to subtract
        if orderpoints:
            subtract_quantity = orderpoints.subtract_procurements_from_orderpoints()
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
                precision_rounding=orderpoint.product_uom.rounding,
            )
            if diff_qty > 0:
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

    @api.multi
    def _compute_average_consumption(self):
        # Stop the method if self is empty.
        # Otherwise SQL query will fail (ids = [])
        if not self:
            return
        today = datetime.now()
        today_minus_one_year = today - relativedelta(years=1)
        today_str = fields.Datetime.to_string(today)
        today_minus_one_year_str = fields.Datetime.to_string(today_minus_one_year)
        # Compute annual consumption
        query_annual = """
        SELECT
          sol.product_id,
          sum(sol.product_uom_qty)
        FROM sale_order_line AS sol
          INNER JOIN sale_order so ON sol.order_id = so.id
        WHERE so.confirmation_date IS NOT NULL
          AND sol.product_id IN %s
          AND so.confirmation_date >= %s
          AND so.confirmation_date < %s
          AND so.state <> 'cancel'
        GROUP BY sol.product_id
        """
        self.env.cr.execute(
            query_annual, (tuple(self.ids), today_minus_one_year_str, today_str)
        )
        annual_consumption_per_products = dict(self.env.cr.fetchall())

        # Compute three months consumption
        last_year_start = (date.today() - relativedelta(years=1)).replace(day=1)
        last_year_start_str = fields.Datetime.to_string(last_year_start)
        last_year_end = last_year_start + relativedelta(months=3)
        last_year_end_str = fields.Datetime.to_string(last_year_end)
        query_period = """
        SELECT
          sol.product_id,
          sum(sol.product_uom_qty)
        FROM sale_order_line AS sol
          INNER JOIN sale_order so ON sol.order_id = so.id
        WHERE so.confirmation_date IS NOT NULL
          AND sol.product_id IN %s
          AND so.confirmation_date >= %s
          AND so.confirmation_date < %s
          AND so.state <> 'cancel'
        GROUP BY sol.product_id
        """
        self.env.cr.execute(
            query_period, (tuple(self.ids), last_year_start_str, last_year_end_str)
        )
        three_months_consumption_per_products = dict(self.env.cr.fetchall())

        for product in self:
            annual_consumption = annual_consumption_per_products.get(product.id, 0)
            if annual_consumption:
                av_annual_consumption = round(float(annual_consumption) / 12, 2)
            else:
                av_annual_consumption = 0
            product.average_annual_consumption = av_annual_consumption

            three_months_consumption = three_months_consumption_per_products.get(
                product.id, 0
            )
            if three_months_consumption:
                av_three_months_consumption = round(
                    float(three_months_consumption) / 3, 2
                )
            else:
                av_three_months_consumption = 0
            product.average_three_months_consumption = av_three_months_consumption

    @api.multi
    def get_lots(self):
        self.ensure_one()

        lots = self.env["stock.production.lot"].search(
            [("product_id", "=", self.id), ("is_archived", "=", False)],
            order="life_date",
        )

        return lots

    @api.multi
    def get_promotions(self):
        self.ensure_one()

        sellers = self.seller_ids
        sellers_with_discount = sellers.filtered(
            lambda s: s.discount_purchase or s.ratio_promotional_product
        )
        sellers_with_discount.sorted(lambda seller: seller.date_start)

        return list(sellers_with_discount)

    @api.multi
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
          to_char(so.confirmation_date, 'YYYY-MM') AS year_month,
          sum(sol.product_uom_qty)
        FROM sale_order_line AS sol
          INNER JOIN sale_order so ON sol.order_id = so.id
        WHERE so.confirmation_date IS NOT NULL
          AND sol.product_id = %s
          AND so.confirmation_date::DATE >= (NOW() - INTERVAL '1 year')::DATE
          AND so.confirmation_date::DATE < NOW()::DATE
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
                label = "%02d/%s" % (month, str(today.year)[2:])
                value = values.get("%s-%02d" % (today.year, month), 0)
                month_values = [{"label": label, "value": value}]
            # If the current month is the same than today
            # (take data in the current year AND in the last year)
            elif month == today.month:
                # We don't take values in the current year if we are the first
                # day of month (there are no data for the current month)
                if today.day == 1:
                    label = "%02d/%s" % (month, str(today.year - 1)[2:])
                    value = values.get("%s-%02d" % (today.year - 1, month), 0)
                    month_values = [{"label": label, "value": value}]
                # Otherwise we take values in the current year and in the last
                # year
                else:
                    label_current_year = "%02d/%02d/%s" % (
                        today.day - 1,
                        month,
                        str(today.year)[2:],
                    )
                    value_current_year = values.get("%s-%02d" % (today.year, month), 0)

                    label_last_year = "%02d/%02d/%s" % (
                        today.day,
                        month,
                        str(today.year - 1)[2:],
                    )
                    value_last_year = values.get("%s-%02d" % (today.year - 1, month), 0)

                    month_values = [
                        {"label": label_current_year, "value": value_current_year},
                        {"label": label_last_year, "value": value_last_year},
                    ]
            # Otherwise we take values in the last year
            else:
                label = "%02d/%s" % (month, str(today.year - 1)[2:])
                value = values.get("%s-%02d" % (today.year - 1, month), 0)
                month_values = [{"label": label, "value": value}]

            graph_values += month_values

        result = [{"key": "Sale order", "values": graph_values}]

        return result
