# -*- coding: utf-8 -*-
# © 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.addons.queue_job.job import job


class ReportAsync(models.AbstractModel):
    _name = 'report.async'

    @api.multi
    def get_report_name(self):
        raise NotImplementedError

    @job(default_channel='root.background.report')  # priority=4
    @api.multi
    def print_and_attach_report(self, report, send_to_fax=None):
        """Print and attach a report.

        param send_to_fax: If not empty the attachment will be sent
        to the number specified.
        """
        self.ensure_one()
        filename = self.get_report_name()
        data = self.env['report'].get_pdf([self.id], report)
        existing = self.env['ir.attachment'].search(
            [('name', '=', filename), ('res_model', '=', self._name)]
        )
        if len(existing):
            existing[0].datas = data.encode('base_64')
        else:
            new_report = self.env['ir.attachment'].create(
                {
                    'type': 'binary',
                    'res_model': self._name,
                    'res_id': self.id,
                    'name': filename,
                    'datas_fname': filename,
                    'mimetype': 'application/pdf',
                    'datas': data.encode('base_64'),
                }
            )
        if send_to_fax:
            report_id = existing[0].id if len(existing) else new_report.id
            fax = self.env.ref('external_fax.ovh')
            fax.with_delay(
                description=_(u'Sending fax for {} with id {}').format(
                    self._name, self.id
                ),
                priority=10,
            ).send(send_to_fax, report_id)
