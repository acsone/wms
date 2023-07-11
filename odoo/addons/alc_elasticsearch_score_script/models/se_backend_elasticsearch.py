# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models


class SeBackendElasticsearch(models.Model):

    _inherit = "se.backend.elasticsearch"

    score_on_position_script = fields.Text(
        help="Script used in ES query to compute the score of query on specific "
        "fields according to the position of searched terms in the field"
    )

    def _get_es_client(self):
        self.ensure_one()
        with self.work_on(self._name, index=None) as work:
            adapter = work.component(usage="se.backend.adapter")
            return adapter._get_es_client()

    @api.model
    def _scrip_field_json(self, value):
        value = "".join(value.replace('"""', '"').split("\n"))
        return json.loads(value)

    def create_or_update_score_on_position_script(self):
        client = self._get_es_client()
        client.put_script(
            "score_on_position", self._scrip_field_json(self.score_on_position_script)
        )
