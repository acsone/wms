# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import float_is_zero

from odoo.addons.sale_stock.models import sale_order


class SaleOrder(sale_order.SaleOrder):
    def refresh_product_qties_unavailable(self):
        """Recompute the product_qty_unavailable on sale order.

        This method return the delta between the previous computed qty
        and the new one by line id.
        """
        self.ensure_one()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        existing_values = {l.id: l.product_qty_unavailable for l in self.order_line}
        new_values = {l.id: l.current_product_qty_unavailable for l in self.order_line}
        to_update = []
        result = {}
        for _id in self.order_line.ids:
            delta = new_values[_id] - existing_values[_id]
            if float_is_zero(delta, precision_digits=precision):
                continue
            to_update.append((1, _id, {"product_qty_unavailable": new_values[_id]}))
            result[_id] = delta
        if to_update:
            self.write({"order_line": to_update})
        return result
