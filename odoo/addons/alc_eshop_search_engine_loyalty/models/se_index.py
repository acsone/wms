# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.connector_search_engine.models.se_index import SeIndex as SeIndexBase

from ..tools.loyalty_program_serializer import LoyaltyProgramSerializer


class SeIndex(SeIndexBase):
    serializer_type = fields.Selection(
        selection_add=[
            ("loyalty_program", "Loyalty Program"),
        ],
        ondelete={"loyalty_program": "cascade"},
    )

    @api.constrains("model_id", "serializer_type")
    def _check_model(self):
        loyalty_program_model = self.env["ir.model"].search(
            [("model", "=", "loyalty.program")], limit=1
        )
        for se_index in self:
            if (
                se_index.serializer_type == "loyalty_program"
                and se_index.model_id != loyalty_program_model
            ):
                raise ValidationError(_("'Serializer Type' must match 'Model'"))

    def _get_serializer(self):
        self.ensure_one()
        if self.serializer_type == "loyalty_program":
            return LoyaltyProgramSerializer()
        return super()._get_serializer()
