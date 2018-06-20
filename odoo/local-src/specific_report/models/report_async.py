# -*- coding: utf-8 -*-
# © 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models
from odoo.addons.queue_job.job import job


class ReportAsync(models.AbstractModel):
    _name = 'report.async'

    @api.multi
    def get_report_name(self):
        raise NotImplementedError

    @job(default_channel='root.background.report')
    @api.multi
    def print_and_attach_report(self, report):
        """Print and attach a report"""
        self.ensure_one()
        filename = self.get_report_name()
        data = self.env['report'].get_pdf([self.id], report)
        existing = self.env['ir.attachment'].search([
            ('name', '=', filename), ('res_model', '=', self._name)])
        if len(existing):
            existing[0].db_datas = data.encode('base_64')
        else:
            self.env['ir.attachment'].create({
                'type': 'binary',
                'res_model': self._name,
                'res_id': self.id,
                'name': filename,
                'datas_fname': filename,
                'mimetype': 'application/pdf',
                'db_datas': data.encode('base_64'),
                })
