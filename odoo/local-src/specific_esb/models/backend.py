# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ESBBackend(models.Model):
    _name = 'esb.backend'
    _description = 'ESB Backend'
    _inherit = 'connector.backend'

    sftp_location = fields.Char(string='SFTP Location')

    def _export(self, model):
        with self.work_on(model) as work:
            exporter = work.component(usage='record.exporter.cron')
            exporter.run()

    def cron_export(self, model):
        self.with_delay()._export(model)
