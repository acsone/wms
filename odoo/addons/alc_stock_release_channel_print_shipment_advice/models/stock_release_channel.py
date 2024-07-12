# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import UserError

from odoo.addons.stock_release_channel_shipment_advice_deliver.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):
    is_action_print_allowed = fields.Boolean(compute="_compute_is_action_print_allowed")

    @api.depends("state")
    def _compute_is_action_print_allowed(self):
        for rec in self:
            rec.is_action_print_allowed = rec.state == "delivered"

    def _check_is_action_print_allowed(self):
        for rec in self:
            if not rec.is_action_print_allowed:
                raise UserError(
                    _(
                        "Action 'Print' is not allowed for channel %(name)s.",
                        name=rec.name,
                    )
                )

    def action_print(self):
        self._check_is_action_print_allowed()
        done_shipment_advices = self.in_process_shipment_advice_ids.filtered(
            lambda s: s.state == "done"
        )
        if done_shipment_advices:
            return self.env.ref(
                "shipment_advice.action_report_shipment_advice"
            ).report_action(done_shipment_advices)
        return {}

    def action_sleep(self):
        self.in_process_shipment_advice_ids.write(
            {"in_release_channel_auto_process": False}
        )
        return super().action_sleep()
