# Copyright 2020 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _

from odoo.addons.shopfloor_batch_automatic_creation.services.cluster_picking import (
    ClusterPicking as ClusterPickingBase,
)


class ClusterPicking(ClusterPickingBase):
    def find_batch(self):
        batches = self._batch_picking_search()
        if not batches and self.env["stock.picking.batch"].search(
            [
                ("user_id", "=", self.env.user.id),
                ("state", "not in", ("done", "cancel", "draft")),
            ]
        ):
            return self._response_for_start(
                message={
                    "message_type": "error",
                    "body": _("This operator is already assigned to a batch"),
                },
            )
        return super().find_batch()

    def _select_a_picking_batch(self, batches):
        batch = super()._select_a_picking_batch(batches)
        if batch.exists() and batch.action_start_allowed:
            batch.action_start()
        return batch

    def unassign(self, picking_batch_id):
        """Cancel.

        Transitions:
        * "start" to work on a new batch
        """
        batch = self.env["stock.picking.batch"].browse(picking_batch_id)
        if batch.exists() and batch.action_cancel_start_allowed:
            batch.action_cancel_start()
        return super().unassign(picking_batch_id)
