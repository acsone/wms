# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        """
        Add promotional product in sale order
        :return:
        """
        # Performance for the method action_confirm is crucial !
        # It's why I used a query to retrieve the same information than
        # the method _select_seller_for_sale
        promotional_product_query = """
        SELECT ratio_main_product, ratio_promotional_product
        FROM product_supplierinfo
        WHERE ratio_promotional_product > 0
          AND (date_start IS NULL or date_start <= NOW())
          AND (date_end IS NULL or date_end >= NOW())
          AND (min_qty_sale = 0 OR min_qty_sale IS NULL OR min_qty_sale <= %s)
          AND product_tmpl_id = %s
        ORDER BY sequence, min_qty_sale desc, price
        LIMIT 1;
        """

        for order in self:
            for line in order.order_line:
                line_uom = line.product_uom
                product_uom = line.product_id.uom_id
                product_qty = line.product_uom_qty

                # If the unit of measure is different than the product' UOM
                # we need to adapt the quantity
                if line_uom != product_uom:
                    product_qty = line_uom._compute_quantity(
                        product_qty, product_uom
                    )

                product_tmpl_id = line.product_id.product_tmpl_id.id

                self.env.cr.execute(promotional_product_query,
                                    (product_qty, product_tmpl_id))
                result = self.env.cr.fetchone()
                if not result:
                    continue

                # Compute the coefficient
                ratio_main_product = result[0]
                ratio_promotional_product = result[1]

                coefficient = int(product_qty / ratio_main_product)
                promotional_product_qty = \
                    coefficient * ratio_promotional_product
                if not promotional_product_qty:
                    continue

                # Create the new line with promotional product
                line.copy(default={
                    'order_id': order.id,
                    'price_unit': 0,
                    'product_uom': product_uom.id,
                    'product_uom_qty': promotional_product_qty,
                    'is_promotional_product': True,
                })

        return super(SaleOrder, self).action_confirm()

    @api.multi
    def action_draft(self):
        """
        Remove promotional product
        :return:
        """
        result = super(SaleOrder, self).action_draft()

        lines_to_remove = self.mapped('order_line')\
            .filtered(lambda line: line.is_promotional_product)
        lines_to_remove.unlink()

        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_promotional_product = fields.Boolean('Promotional product')
