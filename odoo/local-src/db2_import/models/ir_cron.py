# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime, timedelta
from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class IrCron(models.Model):
    _inherit = 'ir.cron'

    @api.model
    def activate_connector(self):
        """Activate the cron jobs related to the connector"""
        cj = self.env.ref('connector_esb.ir_cron_esb_export_pharmacy')
        cj.with_delay().job_activate_cron_export(1, 0)
        cj = self.env.ref('connector_esb.ir_cron_esb_export_promotion_alcyon')
        cj.with_delay().job_activate_cron_export(1, 30)

    @api.multi
    @job(default_channel='root.inventory_init')
    def job_activate_cron_export(self, hour=0, minute=0):
        """Activate cron job setting the next execution call"""
        tomorrow = datetime.today() + timedelta(days=1)
        next_call = tomorrow.replace(hour=hour, minute=minute, second=0)
        self.write({
            'active': True,
            'nextcall': fields.Datetime.to_string(next_call),
        })
