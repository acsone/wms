# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def scan_workstation(self, picking_batch_id=None, barcode=None):
        # If we come back on scan_workstaion, we have to make sure we need to
        # scan a workstation
        batch = self.env["stock.picking.batch"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        result = self._release_batch_for_waiting_availabity_pickings(batch)
        if result:
            return result
        return super().scan_workstation(picking_batch_id, barcode)

    def prepare_unload(self, picking_batch_id):
        batch = self.env["stock.picking.batch"].browse(picking_batch_id)
        if not batch.exists():
            return self._response_batch_does_not_exist()
        if not self.work.menu.scan_workstation:
            result = self._release_batch_for_waiting_availabity_pickings(batch)
            if result:
                return result
        return super().prepare_unload(picking_batch_id)

    def _release_batch_for_waiting_availabity_pickings(self, batch):
        if all(state == "confirmed" for state in batch.picking_ids.mapped("state")):
            batch.action_cancel()
            return self._response_for_start(
                message=self.msg_store.all_waiting_availability()
            )
        return False
