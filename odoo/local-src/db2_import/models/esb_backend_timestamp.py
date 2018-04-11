# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from datetime import datetime
from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class EsbBackend(models.Model):
    _inherit = 'esb.backend.timestamp'

    @api.model
    def reset_timestamp(self):
        esb_stamp = self.env.ref('connector_esb.esb_timestamp_stock_update')
        esb_stamp.with_delay().job_reset_timestamp()

    @api.multi
    @job(default_channel='root.inventory_init')
    def job_reset_timestamp(self):
        self.write({
            'last_export': fields.Datetime.to_string(datetime.today())
        })
