# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.rma.models.rma import Rma as RmaBase


class Rma(RmaBase):
    def _prepare_reception_procurement_vals(self, group=None):
        vals = super()._prepare_reception_procurement_vals(group=group)
        if self.operation_id.return_location_id:
            location = self.operation_id.return_location_id
            customer_location = self.env.ref("stock.stock_location_customers")
            rule = self.env["stock.rule"].search(
                [
                    ("location_src_id", "=", customer_location.id),
                    ("location_dest_id", "=", location.id),
                    ("action", "!=", "push"),
                ],
                limit=1,
            )
            vals["route_ids"] = rule.route_id
        return vals
