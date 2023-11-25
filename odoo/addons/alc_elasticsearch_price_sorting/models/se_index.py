# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime, timedelta

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.connector_search_engine.models.se_index import SeIndex as SeIndexBase

_logger = logging.getLogger(__name__)


class SeIndex(SeIndexBase):
    def _get_es_client(self):
        self.ensure_one()
        return self.backend_id._get_es_client()

    def execute_pipeline_set_current_price(self):
        for record in self:
            client = record._get_es_client()
            try:
                task_def = client.update_by_query(
                    index=record.name.lower(),
                    pipeline="set-current-price",
                    wait_for_completion=False,
                )
            except Exception as e:
                _logger.error(e)
                raise UserError(
                    _("Fail to execute pipeline set current price.\n%(error)s", error=e)
                ) from e
            record._delay_check_task(task_def["task"])

    def _delay_check_task(self, task_id, eta_delay_seconds=60):
        eta = datetime.now() + timedelta(seconds=eta_delay_seconds)
        description = _(
            "Check se-current-price task completion %(task)s for index %(name)s",
            task=task_id,
            name=self.name,
        )
        self.with_delay(eta=eta, description=description)._check_es_task_completion(
            task_id
        )

    def _check_es_task_completion(self, task_id):
        client = self._get_es_client()
        task = client.tasks.get(task_id=task_id, wait_for_completion=False)
        if task.get("status") != 404 and not task.get("completed"):
            self._delay_check_task(task_id)
        return task
