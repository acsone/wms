# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import api, models
from odoo.addons.queue_job.job import job, related_action


class ESBExportable(models.Model):
    _name = 'esb.exportable'

    @api.multi
    @job(default_channel='root.esb')
    @related_action(action='related_action_open_record')
    def esb_export_record(self):
        """Export a record"""
        backend = self.env['esb.backend'].sudo().get_singleton()
        with backend.work_on(self._name) as work:
            exporter = work.component('record.exporter')
            return exporter.run(self)
