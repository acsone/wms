# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date, datetime, time, timedelta

import pytz

from odoo import api, fields

from odoo.addons.alc_stock_release_channel_shipment_advice_toursolver.models import (
    stock_release_channel,
)
from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)

float_to_time = stock_release_channel.float_to_time


class StockReleaseChannel(StockReleaseChannelBase):

    pick_allowed = fields.Boolean(default=True)
    pick_allowed_by_picking_type = fields.Json()
    auto_disallow_pick = fields.Boolean(
        string="Disallow picking automatically",
        help="Disallow picking automatically after ongoing transfers are started",
    )
    auto_allow_pick = fields.Boolean(
        string="Allow picking automatically",
        help="Allow picking automatically after all ongoing transfers are done",
    )
    auto_allow_pick_time_before_leave = fields.Float(
        "Duration before shipment leave to allow picking automatically", default=0.5
    )
    auto_allow_pick_datetime = fields.Datetime(
        "Allow picking automatically at", compute="_compute_auto_allow_pick_datetime"
    )

    @api.depends(
        "planned_start_loading_time",
        "leave_planned_datetime",
        "auto_allow_pick_time_before_leave",
    )
    def _compute_auto_allow_pick_datetime(self):
        datetime_now = datetime.now()
        user_tz = pytz.timezone(self.env.user.tz)
        utc_tz = pytz.timezone("UTC")
        for rec in self:
            hours, minutes = float_to_time(rec.planned_start_loading_time)
            planned_start_loading_time = time(hours, minutes)
            planned_start_loading_datetime = datetime.combine(
                date.today(), planned_start_loading_time
            )
            planned_start_loading_datetime = (
                user_tz.localize(planned_start_loading_datetime)
                .astimezone(utc_tz)
                .replace(tzinfo=None)
            )
            if planned_start_loading_datetime <= datetime_now:
                planned_start_loading_datetime += timedelta(days=1)
            hours, minutes = float_to_time(rec.auto_allow_pick_time_before_leave)
            auto_allow_pick_timedelta = timedelta(hours=hours, minutes=minutes)
            rec.auto_allow_pick_datetime = (
                planned_start_loading_datetime - auto_allow_pick_timedelta
            )

    def button_toggle_pick_allowed(self):
        if self.env.context.get("picking_type_id"):
            self._toggle_pick_allowed_for_picking_type_id(
                self.env.context.get("picking_type_id")
            )
        else:
            self._toggle_pick_allowed_channel()

    def _toggle_pick_allowed_channel(self):
        started = self.filtered("pick_allowed")
        stopped = self - started
        started.write({"pick_allowed": False, "pick_allowed_by_picking_type": False})
        stopped.write({"pick_allowed": True, "pick_allowed_by_picking_type": False})

    def _toggle_pick_allowed_for_picking_type_id(self, picking_type_id: int):
        for rec in self:
            pick_allowed_by_picking_type = (
                dict(rec.pick_allowed_by_picking_type)
                if rec.pick_allowed_by_picking_type
                else {}
            )
            pick_allowed = rec._get_picking_type_pick_allowed(picking_type_id)
            pick_allowed_by_picking_type.update({picking_type_id: not pick_allowed})
            rec.pick_allowed_by_picking_type = pick_allowed_by_picking_type

    def _set_pick_allowed(self, pick_allowed: bool, picking_type=None):
        if picking_type:
            return self._set_pick_allowed_for_picking_type_id(
                picking_type.id, pick_allowed
            )
        self.write({"pick_allowed": pick_allowed})
        return True

    def _set_pick_allowed_for_picking_type_id(
        self, picking_type_id: int, pick_allowed: bool
    ):
        for rec in self:
            pick_allowed_by_picking_type = (
                dict(rec.pick_allowed_by_picking_type)
                if rec.pick_allowed_by_picking_type
                else {}
            )
            pick_allowed_by_picking_type.update({picking_type_id: pick_allowed})
            rec.pick_allowed_by_picking_type = pick_allowed_by_picking_type

    def _get_picking_type_pick_allowed(self, picking_type_id: int):
        self.ensure_one()
        if isinstance(picking_type_id, int):
            picking_type_id = str(picking_type_id)
        if (
            not self.pick_allowed_by_picking_type
            or picking_type_id not in self.pick_allowed_by_picking_type
        ):
            return self.pick_allowed
        return self.pick_allowed_by_picking_type.get(picking_type_id)

    def _get_all_picking_type_ids_pick_allowed(self):
        """For a release channel return all picking types where pick is allowed."""
        self.ensure_one()
        res = []
        for picking_type in self.env["stock.picking.type"].search(
            [("release_channel_can_allow_pick", "=", True)]
        ):
            if self._get_picking_type_pick_allowed(picking_type_id=picking_type.id):
                res.append(picking_type.id)
        return res
