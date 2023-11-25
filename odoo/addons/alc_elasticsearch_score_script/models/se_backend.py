# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields

from odoo.addons.alc_connector_search_engine_put_script_mixin.models.se_backend import (
    SeBackend as SeBackendBase,
)


class SeBackend(SeBackendBase):

    score_on_position_script = fields.Text(
        help="Script used in ES query to compute the score of query on specific "
        "fields according to the position of searched terms in the field"
    )

    def create_or_update_score_on_position_script(self):
        self._put_script("score_on_position", self.score_on_position_script)
