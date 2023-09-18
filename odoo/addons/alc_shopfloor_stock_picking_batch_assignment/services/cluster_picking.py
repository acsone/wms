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
