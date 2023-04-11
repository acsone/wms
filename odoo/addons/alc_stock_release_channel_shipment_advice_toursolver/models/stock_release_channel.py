# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import math
from datetime import date, datetime, time, timedelta

import pytz

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

    leave_planned_time = fields.Float("Planned shipment leave time")
    planned_start_loading_time = fields.Float(
        "Planned Start Loading Time", compute="_compute_planned_start_loading_time"
    )
    leave_planned_datetime = fields.Datetime(
        string="Planned shipment leave date time",
        compute="_compute_leave_planned_datetime",
    )

    @api.depends("leave_planned_time")
    def _compute_leave_planned_datetime(self):
        datetime_now = datetime.now()
        user_tz = pytz.timezone(self.env.user.tz)
        utc_tz = pytz.timezone("UTC")

        for rec in self:
            hours, minutes = float_to_time(rec.leave_planned_time)
            leave_planned_time = time(hours, minutes)
            leave_planned_datetime = datetime.combine(date.today(), leave_planned_time)
            leave_planned_datetime = (
                user_tz.localize(leave_planned_datetime)
                .astimezone(utc_tz)
                .replace(tzinfo=None)
            )
            if leave_planned_datetime <= datetime_now:
                leave_planned_datetime += timedelta(days=1)
            rec.leave_planned_datetime = leave_planned_datetime

    @api.depends("leave_planned_time")
    def _compute_planned_start_loading_time(self):
        task_model = self.env["toursolver.task"]
        backend = task_model._get_default_toursolver_backend()
        duration = backend.loading_duration
        for record in self:
            leave_planned_in_minutes = record.leave_planned_time * 60
            if leave_planned_in_minutes and duration:
                record.planned_start_loading_time = (
                    leave_planned_in_minutes - float(duration)
                ) / 60
            else:
                record.planned_start_loading_time = record.leave_planned_time
