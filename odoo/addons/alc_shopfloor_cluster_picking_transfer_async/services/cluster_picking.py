# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _

from odoo.addons.component.core import Component
from odoo.addons.queue_job.job import identity_exact


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def _unload_end(self, batch, completion_info_popup=None):
        """
        _unload_end in async mode.

        This method in the base class is responsible for checking that all pickings are
        set to 'done.' If one of the pickings isn't, it cut its link with the batch,
        allowing it to be picked later by another batch when it's ready.

        If we are in async mode, these checks cannot be done right away as the picking
        is processed in the background. So, this method simply returns the start page
        to the user and lets each picking perform its own checks and cut the link
        with the batch if needed.
        """
        if not self.work.menu.process_picking_in_background:
            return super()._unload_end(
                batch, completion_info_popup=completion_info_popup
            )
        next_line = self._next_line_for_pick(batch)
        if next_line:
            return self._response_for_start_line(
                next_line,
                message=self.msg_store.batch_transfer_line_done(),
                popup=completion_info_popup,
            )
        batch.state = "done"
        for picking in batch.picking_ids.filtered(
            lambda p: p.state not in ("assigned", "done")
        ):
            self._unload_set_picking_to_done(picking, picking.move_line_ids)
        return self._response_for_start(
            message=self.msg_store.batch_transfer_complete(),
            popup=completion_info_popup,
        )

    def _unload_set_picking_to_done(self, picking, lines):
        """
        If we are in async mode, we call a method in the stock.picking model to perform.

        picking validation and verify that it's indeed set to 'done'. Otherwise,
        the picking will cut its link to the batch.
        """
        if self.work.menu.process_picking_in_background:
            description = _(
                "Validate picking %(picking_name)s", picking_name=picking.display_name
            )
            return picking.with_delay(
                identity_key=identity_exact, description=description
            )._shopfloor_unload_set_picking_to_done(
                lines, self.work.menu.unload_package_at_destination
            )
        return super()._unload_set_picking_to_done(picking, lines)
