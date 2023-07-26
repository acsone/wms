# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields

from odoo.addons.stock_release_channel_shipment_advice.models.shipment_advice import (
    ShipmentAdvice as ShipmentAdviceBase,
)

_logger = logging.getLogger(__name__)


class ShipmentAdvice(ShipmentAdviceBase):
    in_release_channel_auto_process = fields.Boolean(
        readonly=True,
        help="Technical field to flag shipment advice that are in a release channel "
        "auto-process",
        index=True,
    )

    @property
    def _is_auto_process(self) -> bool:
        """We consider that a shipment advice created for a release channel in 'delivering'.

        state should be processed automatically
        In this way we avoid that the release channel keep watching the shipment advice
        creation and process them. Each shipment advice manage its own process and call
        the release channel to notify it when it's done.
        """
        return self.release_channel_id and self.release_channel_id.state in (
            "delivering",
            "delivering_error",
        )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec._is_auto_process:
                rec.with_delay(
                    description=_(
                        "Automatically process the shipment advice %(name)s.",
                        name=rec.name,
                    )
                )._auto_process()
        return records

    def _auto_process(self):
        self.ensure_one()
        if not self._is_auto_process:
            return False
        if not self.arrival_date:
            self.arrival_date = fields.Date.context_today(self)
        self.in_release_channel_auto_process = True
        try:
            self.planned_picking_ids._load_in_shipment(self)
            self.action_confirm()
            self.action_in_progress()
            self.action_done()
        except Exception as error:  # pylint: disable=broad-except
            _logger.error(error)
            self.action_cancel()
            self.planned_picking_ids.move_ids.write({"shipment_advice_id": False})
            return self.release_channel_id._shipment_advice_auto_process_notify_error(
                error, self
            )
        return self.release_channel_id._shipment_advice_auto_process_notify_success()
