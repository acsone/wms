# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from datetime import datetime, timedelta

from odoo import _, models

from odoo.addons.queue_job.job import job


class SeIndex(models.Model):

    _inherit = "se.index"

    def _get_es_client(self):
        self.ensure_one()
        return self.backend_id._get_es_client()

    def execute_pipeline_set_current_price(self):
        for record in self:
            client = record._get_es_client()
            task_def = client.update_by_query(
                index=record.name,
                pipeline="set-current-price",
                wait_for_completion=False,
            )
            record._delay_check_task(task_def["task"])

    def _delay_check_task(self, task_id, eta_delay_seconds=60):
        eta = datetime.now() + timedelta(seconds=eta_delay_seconds)
        description = _("Check se-current-price task completion %s for index %s") % (
            task_id,
            self.name,
        )
        self.with_delay(eta=eta, description=description)._check_es_task_completion(
            task_id
        )

    @job
    def _check_es_task_completion(self, task_id):
        client = self._get_es_client()
        task = client.tasks.get(task_id=task_id, wait_for_completion=False)
        if task.get("status") != 404:
            self._delay_check_task(task_id)
