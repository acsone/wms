from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def unassign(self, picking_batch_id):
        """Cancel.

        Transitions:
        * "start" to work on a new batch
        """
        batch = self.env["stock.picking.batch"].browse(picking_batch_id)
        if batch.exists():
            batch.action_cancel()
        return self._response_for_start()
