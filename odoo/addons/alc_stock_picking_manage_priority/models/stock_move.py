# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.stock_available_to_promise_release.models.stock_move import (
    StockMove as StockMoveBase,
)


class StockMove(StockMoveBase):
    def _after_release_update_chain(self):
        return super(
            StockMove, self.with_context(no_check_priority=True)
        )._after_release_update_chain()

    def _assign_picking_post_process(self, new=False):
        return super(
            StockMove, self.with_context(no_check_priority=True)
        )._assign_picking_post_process(new=new)
