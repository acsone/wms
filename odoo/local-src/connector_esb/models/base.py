# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.addons.component.exception import NoComponentError
from odoo.addons.queue_job.job import job, related_action


class Base(models.AbstractModel):
    """Override base model to add export facilities to all of them."""

    _inherit = 'base'

    @job(default_channel='root.background.esb')  # priority=25
    @related_action(action='related_action_unwrap_binding')
    @api.multi
    def esb_export_record(self, backend, timestamp, fields=None):
        with backend.work_on(self._name, timestamp=timestamp) as work:
            try:
                exporter = work.component(usage='record.exporter')
            except NoComponentError:
                pass
            else:
                exporter.run(self)
