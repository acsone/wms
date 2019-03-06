# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# Copyright 2017 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_confirm(self):
        """Add promotional product in sale order

        For each line in the sale order check if it gives the right
        to some promotional products. And fix the sequence number on the lines
        at the same time.
        """
        if self.env.context.get('__no_promotional_product'):
            return super(SaleOrder, self).action_confirm()
        for order in self:
            if not order.supplier_promotion_allowed:
                continue
            sequence = 1
            for line in order.order_line:
                product_tmpl = line.product_id.product_tmpl_id
                promotional_qty = product_tmpl.get_promotional_product(
                    line.product_uom_qty, line.product_id.uom_id
                )
                line.sequence = sequence
                if not promotional_qty:
                    sequence += 1
                    continue
                line._create_promotional_line(promotional_qty)
                sequence += 2
        return super(SaleOrder, self).action_confirm()

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
        lines_to_remove = self.mapped('order_line').filtered(
            lambda line: line.is_promotional_product
        )
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

    @api.multi
    def _prepare_promotional_line(self, qty):
        self.ensure_one()
        sequence = self.sequence + 1
        return {
            'order_id': self.order_id.id,
            'sequence': sequence,
            'price_unit': 0,
            'product_uom': self.product_id.uom_id.id,
            'product_uom_qty': qty,
            'is_promotional_product': True,
        }

    @api.multi
    def _create_promotional_line(self, qty):
        """Create the new line with promotional product."""
        self.ensure_one()
        values = self._prepare_promotional_line(qty)
        self.copy(default=values)
