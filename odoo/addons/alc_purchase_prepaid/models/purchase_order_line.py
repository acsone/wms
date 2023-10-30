# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

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
            # When no invoice has been created yet and the order is marked as
            # prepayment, then allow to create an invoice based on the ordered
            # quantity
            if (
                line.product_id.purchase_method != "purchase"
                and line.order_id.prepayment
                and line.order_id.state in ["purchase", "done"]
                and not line.qty_invoiced
            ):
                line.qty_to_invoice = line.product_qty
        return True
