# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.tools.float_utils import float_compare

from odoo.addons.purchase.models import purchase


class PurchaseOrderLine(purchase.PurchaseOrderLine):
    @api.depends(
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "qty_received",
        "product_uom_qty",
        "order_id.state",
        "order_id.prepayment",
    )
    def _compute_qty_invoiced(self):
        super()._compute_qty_invoiced()
        for line in self:
            # recompute qty_to_invoice
            qty = 0
            if (
                line.product_id.purchase_method != "purchase"
                and line.order_id.prepayment
                and line.order_id.state in ["purchase", "done"]
            ):
                qty = line.product_qty - line.qty_invoiced
                if (
                    float_compare(
                        qty, 0.0, precision_rounding=line.product_uom.rounding
                    )
                    <= 0
                ):
                    qty = 0.0
            line.qty_to_invoice = qty
        return True
