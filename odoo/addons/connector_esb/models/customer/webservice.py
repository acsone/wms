# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from collections import namedtuple

from odoo import fields

from odoo.addons.component.core import Component

StatsFormOptions = namedtuple(
    "StatsFormOptions", "customer_ref start end product_type suppliers language"
)
# Make None the default value for fields
# customer_ref is required, hence the len(fields) - 1
StatsFormOptions.__new__.__defaults__ = (None,) * (len(StatsFormOptions._fields) - 1)


class StatisticsFormWebserviceMessage(Component):

    _name = "esb.webservice.message.statistics.form"
    _inherit = ["esb.webservice.message.base"]
    _apply_on = ["res.partner"]
    _usage = "ws.message.statistics.form"

    options_for_form = StatsFormOptions

    def _data_for_message(self, options):

        sql = """
SELECT
    pp.default_code AS "sku",

    COALESCE(
        (SELECT value
            FROM ir_translation
            LEFT JOIN res_lang ON ir_translation.lang = res_lang.code
            WHERE res_lang.esb_ref=%s AND
                ir_translation.name='product.template,name' AND
                res_id = pt.id LIMIT 1
        ),
        pt.name
    ) AS "productName",

    CASE business_unit.esb_ref
    WHEN 'ALI' THEN
        'aliment'
    WHEN 'MAT' THEN
        'materiel'
    WHEN 'MED' THEN
        'medicament'
    ELSE
        ''
    END AS "productType",

    STRING_AGG(distinct supplier.ref, ',' ORDER BY supplier.ref)
        AS "manufacturer",

    SUM(sol.qty_delivered) / count(sol.id) AS "qtyDelivered",

    ROUND(SUM(sol.qty_delivered * sol.price_unit) / count(sol.id), 3)
        AS "totalPrice",

    (SELECT SUM(amount)
        FROM account_tax
        LEFT JOIN product_taxes_rel
            ON product_taxes_rel.tax_id = account_tax.id
        WHERE product_taxes_rel.prod_id = pt.id
    )  AS "taxRate"

FROM sale_order_line AS sol
LEFT JOIN product_product AS pp ON sol.product_id = pp.id
LEFT JOIN product_template AS pt ON pp.product_tmpl_id = pt.id

LEFT JOIN LATERAL
    (WITH RECURSIVE parent_category AS (
        SELECT parent_id, esb_ref, is_business_unit
            FROM product_category WHERE id=pt.categ_id
        UNION
        SELECT pcat.parent_id, pcat.esb_ref, pcat.is_business_unit
            FROM product_category AS pcat
            INNER JOIN parent_category p ON p.parent_id = pcat.id
    )
    SELECT esb_ref FROM parent_category WHERE is_business_unit IS TRUE limit 1
    ) business_unit
    ON TRUE

LEFT JOIN sale_order AS so ON sol.order_id = so.id
LEFT JOIN res_partner AS customer ON customer.id = so.partner_id
RIGHT OUTER JOIN product_supplierinfo AS psi
    ON psi.product_tmpl_id = pt.id
LEFT JOIN res_partner AS supplier ON supplier.id = psi.name

WHERE sol.invoice_status = 'invoiced' AND
      customer.ref = %s
        """

        params = []
        params.append(options.language or "FR")
        params.append(options.customer_ref)
        if options.product_type:
            sql += " AND business_unit.esb_ref = %s"
            params.append(options.product_type)
        if options.start:
            sql += " AND so.date_order >= %s"
            params.append(fields.Date.to_string(options.start))
        if options.end:
            sql += " AND so.date_order <= %s"
            params.append(fields.Date.to_string(options.end))
        if options.suppliers:
            sql += " AND supplier.ref in %s"
            params.append(tuple(options.suppliers))
        sql += " GROUP BY pp.id,pp.default_code,business_unit.esb_ref,pt.id;"

        self.env.cr.execute(sql, params)
        data = self.env.cr.fetchall()
        column_names = [column.name for column in self.env.cr.description]
        return [dict(zip(column_names, row)) for row in data]

    def get_message(self, options):
        return self._produce_xml(self._data_for_message(options))


class CustomerDeliveryFeeWebserviceMessage(Component):

    _name = "esb.webservice.message.customer.delivery.fee"
    _inherit = ["esb.webservice.message.base"]
    _apply_on = ["res.partner"]
    _usage = "ws.message.customer.delivery.fee"

    def get_message(self, customer_ref):
        """Always sending the same result !? so no need to call produce.

           As well the structure of the xml without the wrapping
           element makes it difficult to generate with the producer as it is.
           So easier and faster to return what is expected.
        """
        return (
            '<?xml version="1.0" encoding="UTF-8" ?>'
            "<result>"
            "<byPassTestAmount>True</byPassTestAmount>"
            "<totalOrderAmount>9999.00</totalOrderAmount>"
            "</result>"
        )
