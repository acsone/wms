# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging

from odoo import _, api, fields
from odoo.exceptions import UserError

from odoo.addons.connector_elasticsearch.models.se_backend import (
    SeBackend as SeBackendBase,
)

_logger = logging.getLogger(__name__)


class SeBackend(SeBackendBase):

    score_on_position_script = fields.Text(
        help="Script used in ES query to compute the score of query on specific "
        "fields according to the position of searched terms in the field"
    )

    def _get_es_client(self):
        self.ensure_one()
        adapter = self.get_adapter()
        return adapter._es_client

    @api.model
    def _scrip_field_json(self, value):
        value = "".join(value.replace('"""', '"').split("\n"))
        return json.loads(value)

    def create_or_update_score_on_position_script(self):
        client = self._get_es_client()
        try:
            client.put_script(
                "score_on_position",
                self._scrip_field_json(self.score_on_position_script),
            )
        except Exception as e:
            _logger.error(e)
            raise UserError(
                _("Fail to put the score script.\n%(error)s", error=e)
            ) from e
