# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import math

from odoo import api, fields

from odoo.addons.stock_release_channel_shipment_advice_toursolver.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


def float_to_time(hours_minutes: float) -> (int, int):
    hour = math.floor(hours_minutes)
    minute = round((hours_minutes % 1) * 60)
    if minute == 60:
        minute = 0
        hour += 1
    return hour, minute


class StockReleaseChannel(StockReleaseChannelBase):
    loading_duration = fields.Integer(
        string="Loading time",
        help="Loading time in minutes",
        compute="_compute_loading_duration",
        inverse="_inverse_loading_duration",
    )
    planned_start_loading_time = fields.Float(
        "Start loading at", compute="_compute_planned_start_loading_time"
    )
    leave_planned_datetime = fields.Datetime(
        string="Planned shipment leave date time",
        compute="_compute_leave_planned_datetime",
    )

    @api.depends("shipment_advice_departure_time", "loading_duration")
    def _compute_planned_start_loading_time(self):
        for rec in self:
            leave_planned_in_minutes = rec.shipment_advice_departure_time * 60
            if leave_planned_in_minutes and rec.loading_duration:
                rec.planned_start_loading_time = (
                    leave_planned_in_minutes - float(rec.loading_duration)
                ) / 60
            else:
                rec.planned_start_loading_time = rec.shipment_advice_departure_time

    def _compute_loading_duration(self):
        task_model = self.env["toursolver.task"]
        backend = task_model._get_default_toursolver_backend()
        self.update({"loading_duration": backend.loading_duration})

    def _inverse_loading_duration(self):
        task_model = self.env["toursolver.task"]
        backend = task_model._get_default_toursolver_backend()
        backend.loading_duration = self.loading_duration
