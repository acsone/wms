# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.addons.component.core import Component


class ProductCustomerStatWebserviceMessage(Component):

    _name = "esb.webservice.message.product.customer.stat"
    _inherit = ["esb.webservice.message.base"]
    _apply_on = ["sale.order.line"]
    _usage = "ws.message.product.customer.stat"

    def get_message(self, customer_ref, sku):
        """
            Return a customer monthly purchase statistics for a product during
            the last 12 months. Starting from last month.
        """
        periods = {}
        today = date.today()
        date_start = date(today.year - 1, today.month, 1)
        date_end = date(today.year, today.month, 1)
        # Get the sale order line for the customer and specific product
        # for the last 12 month starting from one month before
        sol = self.env["sale.order.line"].search(
            [
                ("order_id.partner_id.ref", "=", customer_ref),
                ("order_id.date_order", ">=", fields.Date.to_string(date_start)),
                ("order_id.date_order", "<", fields.Date.to_string(date_end)),
                ("product_tmpl_id.default_code", "=", sku),
            ]
        )
        # Compute the statistics for each month
        for _m in range(12):
            periods.setdefault(fields.Date.to_string(date_start)[:-3], 0)
            date_start += relativedelta(months=1)
        for line in sol:
            period = line.order_id.date_order[:7]
            periods[period] += line.product_uom_qty
        data = [
            {"salesPeriod": month, "salesAverage": "{:.2f}".format(qty)}
            for month, qty in periods.iteritems()
        ]
        return self._produce_xml(data)


class ProductCategoryWebserviceMessage(Component):

    _name = "esb.webservice.message.product.category"
    _inherit = ["esb.webservice.message.base"]
    _apply_on = ["sale.order.line"]
    _usage = "ws.message.customer.stat"

    def get_message(self, customer_ref):
        sql = """
SELECT
    CASE esb_ref
        WHEN 'ALI' THEN
            'aliment'
        WHEN 'MAT' THEN
            'materiel'
        WHEN 'MED' THEN
            'medicament'
        ELSE
            ''
    END AS "productType",
    CAST(ROUND(SUM("purchaseYear"), 2) AS TEXT) AS "purchaseYear",
    CAST(ROUND(SUM("purchaseLastYear"), 2) AS TEXT) AS "purchaseLastYear"
FROM
        (
    SELECT
        sol.id,
        sol.state,
        sol.name,
        business_unit.esb_ref,
        CASE (EXTRACT(YEAR FROM current_date) -
              EXTRACT(YEAR FROM so.date_order::date))
        WHEN 0 THEN
            sum(sol.qty_delivered * price_reduce_taxexcl) / count(sol.id)
        ELSE
            0
        END AS "purchaseYear",

        CASE (EXTRACT(YEAR FROM current_date) -
              EXTRACT(YEAR FROM so.date_order::date))
        WHEN 1 THEN
            sum(sol.qty_delivered * price_reduce_taxexcl) / count(sol.id)
        ELSE
            0
        END AS "purchaseLastYear"

    FROM sale_order_line AS sol
    LEFT JOIN sale_order AS so ON sol.order_id = so.id
    LEFT JOIN product_product AS pp ON sol.product_id = pp.id
    LEFT JOIN product_template AS pt ON pp.product_tmpl_id = pt.id
    LEFT JOIN res_partner AS customer ON customer.id = so.partner_id

    LEFT JOIN LATERAL
(
WITH RECURSIVE parent_category AS (
    SELECT parent_id, esb_ref, is_business_unit
        FROM product_category
        WHERE id=pt.categ_id
    UNION
    SELECT pcat.parent_id, pcat.esb_ref, pcat.is_business_unit
        FROM product_category AS pcat
        INNER JOIN parent_category p ON p.parent_id = pcat.id
)
SELECT esb_ref FROM parent_category WHERE is_business_unit IS TRUE limit 1
) business_unit
    ON TRUE

    WHERE customer.ref = %s
          AND so.state not in ('cancel', 'draft')
          AND (EXTRACT(YEAR FROM current_date) -
               EXTRACT(YEAR FROM so.date_order::date) < 2)

    GROUP BY sol.id, so.date_order, pt.categ_id, business_unit.esb_ref
    ) AS "resultset"

WHERE esb_ref<>''
GROUP BY esb_ref;

        """
        self.env.cr.execute(sql, [customer_ref])
        raw_data = self.env.cr.fetchall()
        column_names = [column.name for column in self.env.cr.description]
        data = [dict(zip(column_names, row)) for row in raw_data]
        return self._produce_xml(data, list_item_el="resultItem")
