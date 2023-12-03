# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
            return
        picking_lines = self.move_line_ids
        if all(line.shopfloor_unloaded for line in picking_lines):
            self._action_done()
        if self.state != "done" and self.batch_id:
            # Unassign not validated pickings from the batch, they will be
            # processed in another batch automatically later on
            self.write({"batch_id": False, "user_id": False, "printed": False})
        if unload_package_at_destination:
            lines.result_package_id = False
