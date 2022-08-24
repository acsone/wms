# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from datetime import datetime

import pytz

from odoo import _, api, fields, models

from odoo.addons.delivery_rounds.models.round_instance import float2time
from odoo.addons.queue_job.job import identity_exact, job


class RoundInstance(models.Model):

    _inherit = "round.instance"
    picking_med_launched = fields.Boolean(
        "Pickings Med Launched", readonly=True, track_visibility="onchange",
    )
    picking_ali_launched = fields.Boolean(
        "Pickings Ali Launched", readonly=True, track_visibility="onchange",
    )
    picking_mat_launched = fields.Boolean(
        "Pickings Mat Launched", readonly=True, track_visibility="onchange",
    )
    picking_frigo_launched = fields.Boolean(
        "Pickings Frigo Launched", readonly=True, track_visibility="onchange",
    )
    picking_launched = fields.Boolean(
        "Pickings Launched",
        compute="_compute_picking_launched",
        inverse="_inverse_picking_launched",
        store=True,
    )
    auto_close_picking_launched = fields.Boolean(
        string="Auto close picking launched", default=False
    )
    time_reopen_picking_launched = fields.Float(
        "Duration before departure to re open pickings", default=0.5
    )

    def write(self, vals):
        res = super(RoundInstance, self).write(vals)
        if (
            "time_leave_planned" in vals
            or "auto_close_picking_launched" in vals
            or "time_reopen_picking_launched" in vals
        ):
            # First delete previous job
            self._delete_previous_existing_job_if_required()
            # Then create new job
            self._delay_reopen_pickings_if_required()
        return res

    def _delete_previous_existing_job_if_required(self):
        # Retrieve jobs already started for the round instance
        self.env.cr.execute(
            """
                        SELECT id from queue_job
                            WHERE model_name = %(model)s
                            AND method_name = %(method)s
                            AND record_ids = %(ids)s
                            AND state = %(state)s
                        """,
            {
                "model": "round.instance",
                "method": "_reopen_pickings",
                "ids": json.dumps(self.ids),
                "state": "pending",
            },
        )
        result = self.env.cr.fetchall()
        ids = [r[0] for r in result]
        jobs_to_delete = self.env["queue.job"].browse(ids)
        # In v14, state cancelled exists on jobs and we could use jobs_to_delete.button_cancelled()
        # to cancel the previous job while keeping the history.
        # In v10 : cancelled does not exist... So let's put the state to DONE with an explicit reason
        if jobs_to_delete:
            jobs_to_delete.action_done(
                reason="Change on hours for delivery rounds or autoclosing config. This job is set to done, a new one is created."
            )

    def _delay_reopen_pickings_if_required(self):
        for rec in self:
            if rec.auto_close_picking_launched and rec.time_reopen_picking_launched:
                description = (
                    _("%s : Automatic reopening of pickings in delivery round.")
                    % rec.display_name
                )
                float_start_time_reopen = (
                    rec.geo_optimization_planned_start_loading_time
                    - rec.time_reopen_picking_launched
                )
                start_time_reopen = float2time(float_start_time_reopen)
                eta_str = rec.date + " " + start_time_reopen
                eta_time = datetime.strptime(eta_str, "%Y-%m-%d %H:%M")
                # The time is the time in local zone
                # eta should be in utc
                # We must therefore convert from expected locale to  utc
                bru_tz = pytz.timezone("Europe/Brussels")
                utc_tz = pytz.timezone("UTC")
                eta_time = bru_tz.localize(eta_time).astimezone(utc_tz)
                # priority 3 : those jobs should be processed first
                rec.with_delay(
                    eta=eta_time,
                    priority=3,
                    identity_key=identity_exact,
                    description=description,
                )._reopen_pickings()

    @job(default_channel="root.background.reopen_pickings")
    def _reopen_pickings(self):
        for rec in self:
            rec.write({"picking_launched": True})

    def button_resetdraft(self):
        res = super(RoundInstance, self).button_resetdraft()
        self._delay_reopen_pickings_if_required()
        return res

    def _toggle_by_zone(self, picking_launched_to_toggle):
        started = self.filtered(picking_launched_to_toggle)
        stopped = self - started
        started._picking_stop_by_zone(picking_launched_to_toggle)
        stopped._picking_start_by_zone(picking_launched_to_toggle)

    def toggle_picking_med_launched(self):
        self._toggle_by_zone("picking_med_launched")

    def toggle_picking_ali_launched(self):
        self._toggle_by_zone("picking_ali_launched")

    def toggle_picking_frigo_launched(self):
        self._toggle_by_zone("picking_frigo_launched")

    def toggle_picking_mat_launched(self):
        self._toggle_by_zone("picking_mat_launched")

    def _picking_start_by_zone(self, picking_launched_to_toggle):
        """ Pickings can be processed """
        for rec in self:
            rec.write({picking_launched_to_toggle: True})

    def _picking_stop_by_zone(self, picking_launched_to_toggle):
        """ Pickings cannot be processed """
        for rec in self:
            rec.write({picking_launched_to_toggle: False})

    @api.depends(
        "picking_mat_launched",
        "picking_ali_launched",
        "picking_med_launched",
        "picking_frigo_launched",
    )
    def _compute_picking_launched(self):
        for rec in self:
            if (
                rec.picking_ali_launched
                or rec.picking_med_launched
                or rec.picking_frigo_launched
                or rec.picking_mat_launched
            ):
                rec.picking_launched = True
            if (
                not rec.picking_ali_launched
                and not rec.picking_med_launched
                and not rec.picking_frigo_launched
                and not rec.picking_mat_launched
            ):
                rec.picking_launched = False

    def _inverse_picking_launched(self):
        for rec in self:
            if rec.picking_launched:
                rec.write(
                    {
                        "picking_med_launched": True,
                        "picking_ali_launched": True,
                        "picking_mat_launched": True,
                        "picking_frigo_launched": True,
                    }
                )
            else:
                rec.write(
                    {
                        "picking_med_launched": False,
                        "picking_ali_launched": False,
                        "picking_mat_launched": False,
                        "picking_frigo_launched": False,
                    }
                )

    @api.model
    def create(self, vals):
        if "template_id" in vals:
            template = self.env["round.template"].browse(vals["template_id"])
            if "auto_close_picking_launched" not in vals:
                vals[
                    "auto_close_picking_launched"
                ] = template.auto_close_picking_launched
            if "time_reopen_picking_launched" not in vals:
                vals[
                    "time_reopen_picking_launched"
                ] = template.time_reopen_picking_launched
        return super(RoundInstance, self).create(vals)
