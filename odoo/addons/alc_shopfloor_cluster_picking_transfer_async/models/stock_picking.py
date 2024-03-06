# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    def _shopfloor_unload_set_picking_to_done(
        self, lines, unload_package_at_destination
    ):
        """
        This method is called with a delay to set pickings to 'done.'.

        At this stage, we assume the batch is set to 'done', and each picking should
        perform its own checks:
        - If the picking is not set to 'done' after '_action_done,'
            - cut the link with the batch
            - unassign the user.
        - Unload line packages.
        """
        self.ensure_one()
        if self.state in ("done", "cancel"):
            return _("Nothing to do. Picking is in %(state)s", state=self.state)
        picking_lines = self.move_line_ids
        all_lines_unloaded = all(line.shopfloor_unloaded for line in picking_lines)
        if lines and unload_package_at_destination and all_lines_unloaded:
            lines.result_package_id = False
        if all_lines_unloaded:
            self._action_done()
        if self.state != "done" and self.batch_id and self.batch_id.state == "done":
            # Unassign not validated pickings from the batch, they will be
            # processed in another batch automatically later on
            self.write({"batch_id": False, "user_id": False, "printed": False})
            return _(
                "Picking unlinked from the batch. Picking is in %(state)s and the batch is done",
                state=self.state,
            )
        return _(
            "Picking state: %(state)s, batch state %(batch_state)s",
            state=self.state,
            batch_state=self.batch_id.state,
        )
