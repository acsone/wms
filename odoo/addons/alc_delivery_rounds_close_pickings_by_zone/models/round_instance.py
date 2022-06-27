# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo import api, fields, models

from odoo.addons.delivery_rounds.models.round_instance import float2time
from odoo.addons.queue_job.job import job


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

    def _delay_reopen_pickings(self):
        for rec in self:
            float_start_time_reopen = (
                rec.time_leave_planned - rec.template_id.time_reopen_picking_lauched
            )
            start_time_reopen = float2time(float_start_time_reopen)
            eta_str = rec.date + " " + start_time_reopen
            eta = datetime.strptime(eta_str, "%Y-%m-%d %H:%M")
            rec.with_delay(eta=eta, priority=99)._reopen_pickings()

    @job(default_channel="root.background.reopen_pickings")  # priority = 99
    def _reopen_pickings(self):
        for rec in self:
            rec.write({"picking_launched": True})

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
