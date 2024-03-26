# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import threading

from odoo.addons.stock_move_auto_assign.models import stock_move


class StockMove(stock_move.StockMove):
    def _action_cancel(self):
        self_ctx = self.with_context(called_action_cancel=True)
        return super(StockMove, self_ctx)._action_cancel()

    def _prepare_auto_assign(self, location_field):
        if self.env.context.get("called_action_cancel") and (
            getattr(threading.current_thread(), "testing", True)
            or self.env.registry.in_test_mode()
        ):
            # we avoid recursive call in case where and additional move is created
            # on assign and therefore cancel existing additional move that will
            # execute the auto assign job (since queue_job are executed in the same
            # process)
            return None
        return super()._prepare_auto_assign(location_field)
