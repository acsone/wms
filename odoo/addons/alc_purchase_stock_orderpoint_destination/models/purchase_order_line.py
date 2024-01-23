# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.purchase.models.purchase import (
    PurchaseOrderLine as PurchaseOrderLineBase,
)


class PurchaseOrderLine(PurchaseOrderLineBase):
    def _prepare_stock_move_vals(
        self, picking, price_unit, product_uom_qty, product_uom
    ) -> dict:
        """
        Override the destination location for generated moves.

        It should be the default reception location of Warehouse and
        not the orderpoint one
        """
        values = super()._prepare_stock_move_vals(
            picking=picking,
            price_unit=price_unit,
            product_uom_qty=product_uom_qty,
            product_uom=product_uom,
        )
        values.update(
            {
                "location_dest_id": self.order_id._get_destination_location(),
            }
        )
        return values
