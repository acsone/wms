# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.alc_stock_release_channel_deliver.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):
    def _toursolver_task_auto_process_notify_error(self, error, related_object):
        self.ensure_one()
        if self.state == "delivering_error":
            return
        self.action_delivering_error()
        self.delivering_error = self._get_delivering_error_message(
            error, related_object
        )
