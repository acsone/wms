# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api

from odoo.addons.sale_stock.models.sale_order_line import (
    SaleOrderLine as SaleOrderLineBase,
)


class SaleOrderLine(SaleOrderLineBase):
    def _get_expected_date_by_product_warehouse(self):
        """Return a dictionary by line id of the forecast_expected_date."""
        groups = self.env["stock.move"].read_group(
            [
                ("product_id", "in", self.product_id.ids),
                ("warehouse_id", "in", self.warehouse_id.ids),
                ("picking_type_id.code", "=", "incoming"),
                ("state", "=", "assigned"),
            ],
            fields=["date:min"],
            groupby=["product_id", "warehouse_id"],
            lazy=False,
        )
        return {
            (group.get("warehouse_id")[0], group.get("product_id")[0]): group.get(
                "date"
            )
            for group in groups
        }

    @api.depends(
        "product_id",
        "order_id.warehouse_id",
        "customer_lead",
        "product_uom_qty",
        "product_uom",
        "order_id.commitment_date",
        "move_ids",
        "move_ids.forecast_expected_date",
        "move_ids.forecast_availability",
    )
    def _compute_qty_at_date(self):
        res = super()._compute_qty_at_date()
        expected_date_by_product_warehouse = (
            self._get_expected_date_by_product_warehouse()
        )
        for rec in self:
            rec.forecast_expected_date = expected_date_by_product_warehouse.get(
                (rec.warehouse_id.id, rec.product_id.id)
            )
        return res
