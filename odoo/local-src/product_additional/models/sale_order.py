# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from operator import itemgetter
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        """
        Add promotional product in sale order
        :return:
        """

        if self.env.context.get('__no_promotional_product'):
            return super(SaleOrder, self).action_confirm()

        for order in self:
            for line in order.order_line:
                line_uom = line.product_uom
                product_uom = line.product_id.uom_id
                product_qty = line.product_uom_qty

                # If the unit of measure is different than the product's UOM
                # we need to adapt the quantity
                if line_uom != product_uom:
                    product_qty = line_uom._compute_quantity(
                        product_qty, product_uom
                    )

                product_tmpl_id = line.product_id.product_tmpl_id.id

                # As sale orders are now confirmed in background,
                # action_confirm performance is not such an issue as before -
                # we can switch back from raw sql to orm
                result = self.env["product.supplierinfo"].search(
                    [
                        ("ratio_promotional_product", ">", 0),
                        ("ratio_main_product", ">", 0),
                        "|",
                        ("date_start", "=", False),
                        ("date_start", "<=", fields.Date.today()),
                        "|",
                        ("date_end", "=", False),
                        ("date_end", ">=", fields.Date.today()),
                        "|",
                        ("min_qty_sale", "=", False),
                        ("min_qty_sale", "<=", product_qty),
                        ("product_tmpl_id", "=", product_tmpl_id)
                    ],
                    limit=1,
                )
                if not result:
                    continue

                # Compute the coefficient
                ratio_main_product = result.ratio_main_product
                ratio_promotional_product = result.ratio_promotional_product

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
        res = super(SaleOrder, self).action_confirm()
        # recompute lines sequences
        for order in self:
            lines = self.env["sale.order.line"].search(
                [("order_id", "=", order.id),],
            )
            lines = sorted(lines, key=itemgetter("sequence", "id"))
            for rec in enumerate(lines, 1):
                rec[1].sequence = rec[0]
        return res

    @api.multi
    def action_draft(self):
        """
        Remove promotional product
        :return:
        """
        result = super(SaleOrder, self).action_draft()
        self._remove_promotional_lines()
        return result

    @api.multi
    def _remove_promotional_lines(self):
        lines_to_remove = self.mapped('order_line')\
            .filtered(lambda line: line.is_promotional_product)
        lines_to_remove.unlink()

    @api.multi
    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        res = super(SaleOrder, self).copy_data(default=default)
        # Skip promotional lines on duplicate
        if 'order_line' in res[0]:
            for i, line in reversed(list(enumerate(res[0]['order_line']))):
                if line[0] == 0 and line[2].get('is_promotional_product'):
                    del res[0]['order_line'][i]
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_promotional_product = fields.Boolean('Promotional product')
