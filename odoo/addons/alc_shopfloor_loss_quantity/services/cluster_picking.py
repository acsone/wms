# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopfloor.services.cluster_picking import (
    ClusterPicking as ClusterPickingBase,
)


class ClusterPicking(ClusterPickingBase):
    def stock_issue(self, picking_batch_id, move_line_id):
        batch = self.env["stock.picking.batch"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        move_line = self.env["stock.move.line"].browse(move_line_id)
        if not move_line.exists():
            return self._pick_next_line(
                batch, message=self.msg_store.operation_not_found()
            )
        if not move_line.is_action_loss_qty_allowed:
            return self._pick_next_line(
                batch, message=self.msg_store.operation_loss_quantity_not_allowed()
            )
        move_line.action_loss_quantity()
        return self._pick_next_line(batch)
