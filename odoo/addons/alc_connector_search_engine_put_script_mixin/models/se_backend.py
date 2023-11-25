# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
import logging

from odoo import _, api
from odoo.exceptions import UserError

from odoo.addons.connector_search_engine.models.se_backend import (
    SeBackend as SeBackendBase,
)

_logger = logging.getLogger(__name__)


class SeBackend(SeBackendBase):
    def _get_es_client(self):
        self.ensure_one()
        adapter = self.get_adapter()
        return adapter._es_client

    @api.model
    def _scrip_field_json(self, value):
        value = "".join(value.replace('"""', '"').split("\n"))
        return json.loads(value)

    def _put_script(self, script_name, script_value):
        client = self._get_es_client()
        try:
            client.put_script(
                script_name,
                self._scrip_field_json(script_value),
            )
        except Exception as e:
            _logger.error(e)
            raise UserError(
                _(
                    "Fail to put the %(script) script.\n%(error)s",
                    script=script_name,
                    error=e,
                )
            ) from e
