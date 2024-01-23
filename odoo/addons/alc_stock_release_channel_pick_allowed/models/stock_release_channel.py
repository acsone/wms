# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta

import pytz

from odoo import api, fields

from odoo.addons.alc_stock_release_channel_shipment_advice_toursolver.models import (
    stock_release_channel,
)
from odoo.addons.queue_job.fields import JobEncoder
from odoo.addons.stock_release_channel.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)

float_to_time = stock_release_channel.float_to_time


class StockReleaseChannel(StockReleaseChannelBase):

    pick_allowed = fields.Boolean(default=True)
    pick_allowed_by_picking_type = fields.Json()
    auto_disallow_pick = fields.Boolean(
        string="Disallow picking automatically",
        help="Prevent automatic picking once the shipment has been started.",
    )
    auto_allow_pick = fields.Boolean(
        string="Allow picking automatically",
        help="Enable automatic picking once the shipment has been completed.",
    )
    auto_allow_pick_time_before_leave = fields.Float(
        "Duration before shipment load to allow picking automatically",
        default=0.5,
        inverse="_inverse_auto_allow_pick_time_before_leave",
    )
    auto_allow_pick_datetime = fields.Datetime(
        "Allow picking automatically at", compute="_compute_auto_allow_pick_datetime"
    )

    @api.depends(
        "planned_start_loading_time",
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
        picking_type_ids = (
            self.env["stock.picking.type"]
            .search([("release_channel_can_allow_pick", "=", True)])
            .ids
        )
        started = self.filtered("pick_allowed")
        stopped = self - started
        started.write(
            {
                "pick_allowed": False,
                "pick_allowed_by_picking_type": {
                    p_id: False for p_id in picking_type_ids
                },
            }
        )
        stopped.write(
            {
                "pick_allowed": True,
                "pick_allowed_by_picking_type": {
                    p_id: True for p_id in picking_type_ids
                },
            }
        )

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
            picking_types_states = rec._get_all_picking_type_ids_state()
            if any(picking_types_states.values()):
                # if any picking_type is enabled, the channel should be enabled
                rec.pick_allowed = True
            else:
                # if all picking_type are disabled, the channel should be disabled
                rec.pick_allowed = False

    def _set_pick_allowed(self, pick_allowed: bool, picking_type=None):
        self.ensure_one()
        if picking_type:
            return self._set_pick_allowed_for_picking_type_id(
                picking_type.id, pick_allowed
            )
        picking_type_ids = (
            self.env["stock.picking.type"]
            .search([("release_channel_can_allow_pick", "=", True)])
            .ids
        )
        self.pick_allowed = pick_allowed
        self.pick_allowed_by_picking_type = {
            p_id: pick_allowed for p_id in picking_type_ids
        }
        return True

    def _set_pick_allowed_for_picking_type_id(
        self, picking_type_id: int, pick_allowed: bool
    ):
        self.ensure_one()
        if self._get_picking_type_pick_allowed(picking_type_id) == pick_allowed:
            return
        pick_allowed_by_picking_type = (
            dict(self.pick_allowed_by_picking_type)
            if self.pick_allowed_by_picking_type
            else {}
        )
        pick_allowed_by_picking_type.update({picking_type_id: pick_allowed})
        self.pick_allowed_by_picking_type = pick_allowed_by_picking_type

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

    def _get_all_picking_type_ids_state(self):
        """For a release channel return all picking types where pick is allowed."""
        self.ensure_one()
        res = {}
        for picking_type in self.env["stock.picking.type"].search(
            [("release_channel_can_allow_pick", "=", True)]
        ):
            res[picking_type.id] = self._get_picking_type_pick_allowed(
                picking_type_id=picking_type.id
            )
        return res

    def _delay_set_pick_allowed(
        self, pick_allowed: bool, picking_type=None, eta: datetime = None
    ):
        self.ensure_one()
        self.with_delay(eta=eta)._set_pick_allowed(
            pick_allowed=pick_allowed, picking_type=picking_type
        )

    def _inverse_auto_allow_pick_time_before_leave(self):
        """
        Auto_allow_pick_datetime changed, we look if there is planned jobs to set.

        pick_allowed True and reschedule them
        """
        for rec in self:
            rec._requeue_set_pick_allowed_true_job()

    def _inverse_shipment_advice_departure_time(self):
        res = super()._inverse_shipment_advice_departure_time()
        for rec in self:
            rec._requeue_set_pick_allowed_true_job()
        return res

    def _get_set_pick_allowed_true_pending_jobs(self):
        self.ensure_one()
        return (
            self.env["queue.job"]
            .search(
                [
                    ("model_name", "=", self._name),
                    ("method_name", "=", "_set_pick_allowed"),
                    ("state", "=", "pending"),
                    ("records", "=", json.dumps(self, cls=JobEncoder)),
                ]
            )
            .filtered(lambda job_: job_.kwargs.get("pick_allowed"))
        )

    def _requeue_set_pick_allowed_true_job(self):
        self.ensure_one()
        for job in self._get_set_pick_allowed_true_pending_jobs():
            job._change_job_state(
                state="done",
                result="Change on hours for release channel pick allowed."
                "This job is set to done, a new one is created.",
            )
            self._delay_set_pick_allowed(
                **job.kwargs, eta=self.auto_allow_pick_datetime
            )

    def action_wake_up(self):
        for rec in self:
            if not rec.auto_allow_pick:
                continue
            rec._delay_set_pick_allowed(
                pick_allowed=True, picking_type=None, eta=rec.auto_allow_pick_datetime
            )
        return super().action_wake_up()

    def action_sleep(self):
        for rec in self:
            if not rec.auto_disallow_pick:
                continue
            rec._set_pick_allowed(pick_allowed=False, picking_type=None)
        return super().action_sleep()

    @api.model
    def _get_channels_pick_allowed(self, picking_types):
        """Return all channels that allows picking for a given picking types."""
        res = self.browse()
        for rec in self.search([("state", "in", ("open", "locked"))]):
            if any(
                rec._get_picking_type_pick_allowed(picking_type.id)
                for picking_type in picking_types
            ):
                res += rec
        return res

    def write(self, vals):
        with self._log_pick_allowed_changes(vals):
            res = super().write(vals)
        return res

    @contextmanager
    def _log_pick_allowed_changes(self, vals):
        log_changes = "pick_allowed_by_picking_type" in vals
        log_values = []
        if log_changes:
            original_values = {r.id: r.pick_allowed_by_picking_type or {} for r in self}
        yield
        if log_changes:
            for rec in self:
                old_value = original_values[rec.id]
                new_value = rec.pick_allowed_by_picking_type or {}
                for picking_type_id, pick_allowed in new_value.items():
                    if (
                        picking_type_id not in old_value
                        or pick_allowed != old_value[picking_type_id]
                    ):
                        log_values.append(
                            {
                                "release_channel_id": rec.id,
                                "picking_type_id": int(picking_type_id),
                                "allowed": pick_allowed,
                            }
                        )
        if log_values:
            self.env["stock.release.channel.pick.allowed.log"].sudo().create(log_values)
