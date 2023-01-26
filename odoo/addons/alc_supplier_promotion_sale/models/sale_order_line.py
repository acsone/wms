# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.models.sale_order_line import SaleOrderLine as SaleOrderLineBase


class SaleOrderLine(SaleOrderLineBase):

    is_promotional_product = fields.Boolean(string="Promotional product")

    def _prepare_promotional_line(self, qty):
        self.ensure_one()
        sequence = self.sequence + 1
        return {
            "order_id": self.order_id.id,
            "sequence": sequence,
            "price_unit": 0,
            "product_uom": self.product_id.uom_id.id,
            "product_uom_qty": qty,
            "is_promotional_product": True,
        }

    def _create_promotional_line(self, qty):
        """Create the new line with promotional product."""
        self.ensure_one()
        values = self._prepare_promotional_line(qty)
        self.copy(default=values)

    def _get_delivered_qty(self):
        """Computes the delivered quantity on sale order lines, based on done.

        stock moves related to its procurements but excluding moves related
        to another product (additional products...)
        """
        self.ensure_one()
        qty = super()._get_delivered_qty()
        for move in self.procurement_ids.mapped("move_ids").filtered(
            lambda r: r.state == "done" and r.is_additional_move
        ):
            if move.location_dest_id.usage == "customer":
                if not move.origin_returned_move_id or (
                    move.origin_returned_move_id and move.to_refund_so
                ):
                    qty -= move.product_uom._compute_quantity(
                        move.product_uom_qty, self.product_uom
                    )
            elif move.location_dest_id.usage != "customer" and move.to_refund_so:
                qty += move.product_uom._compute_quantity(
                    move.product_uom_qty, self.product_uom
                )
        return qty
