# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields

from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def _last_picked_line(self, picking):
        res = super()._last_picked_line(picking)
        if self.work.menu.group_pickings_by_partner:
            # Retrieve pickings for the current batch and for the same partner
            pickings = self.env["stock.picking"].search(
                [
                    ("batch_id", "=", picking.batch_id.id),
                    ("partner_id", "=", picking.partner_id.id),
                ]
            )
            # Get the last picked line for these pickings
            return fields.first(
                pickings.move_line_ids.filtered(
                    lambda l: l.qty_done > 0
                    and l.result_package_id
                    # if we are moving the entire package, we shouldn't
                    # add stuff inside it, it's not a new package
                    and l.package_id != l.result_package_id
                ).sorted(key="write_date", reverse=True)
            )
        return res

    def _check_picking_condition(self, bin_package, move_line):
        return self.work.menu.group_pickings_by_partner and any(
            ml.picking_id.partner_id != move_line.picking_id.partner_id
            for ml in bin_package.planned_move_line_ids.filtered(
                lambda x: x.state not in ("done", "cancel")
            )
        )

    def scan_destination_pack(self, picking_batch_id, move_line_id, barcode, quantity):
        batch = self.env["stock.picking.batch"].browse(picking_batch_id)
        move_line = self.env["stock.move.line"].browse(move_line_id)
        search = self._actions_for("search")
        bin_package = search.package_from_scan(barcode)
        if not batch or not move_line or not bin_package:
            return super().scan_destination_pack(
                picking_batch_id, move_line_id, barcode, quantity
            )
        if self.work.menu.group_pickings_by_partner:
            if self._check_picking_condition(bin_package, move_line):
                return self._response_for_scan_destination(
                    move_line,
                    message={
                        "message_type": "error",
                        "body": _(
                            "The destination bin {} is not empty, please take another."
                        ).format(bin_package.name),
                    },
                    qty_done=quantity,
                )
        return super().scan_destination_pack(
            picking_batch_id, move_line_id, barcode, quantity
        )
