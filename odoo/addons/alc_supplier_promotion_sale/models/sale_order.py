# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.sale.models.sale_order import SaleOrder as SaleOrderBase


class SaleOrder(SaleOrderBase):
    def action_confirm(self):
        """Add promotional product in sale order.

        For each line in the sale order check if it gives the right
        to some promotional products. And fix the sequence number on the lines
        at the same time.
        """
        if self.env.context.get("__no_promotional_product"):
            return super().action_confirm()
        for rec in self:
            if not rec.supplier_promotion_allowed:
                continue
            sequence = 1
            for line in rec.order_line.filtered(lambda x: not x.display_type):
                product_tmpl = line.product_id.product_tmpl_id
                promotional_qty = product_tmpl.get_promotional_product(
                    line.product_uom_qty, line.product_id.uom_id, rec.partner_id
                )
                line.sequence = sequence
                if not promotional_qty:
                    sequence += 1
                    continue
                line._create_promotional_line(promotional_qty)
                sequence += 2
        return super().action_confirm()

    def action_draft(self):
        """
        Remove promotional product.

        :return:
        """
        result = super().action_draft()
        self._remove_promotional_lines()
        return result

    def _remove_promotional_lines(self):
        lines_to_remove = self.mapped("order_line").filtered("is_promotional_product")
        lines_to_remove.unlink()

    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        res = super().copy_data(default=default)
        # Skip promotional lines on duplicate
        if "order_line" in res[0] and res[0]["order_line"]:
            for i, line in reversed(list(enumerate(res[0]["order_line"]))):
                if not line[0] and line[2].get("is_promotional_product"):
                    del res[0]["order_line"][i]
        return res
