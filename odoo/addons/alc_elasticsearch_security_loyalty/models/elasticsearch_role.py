# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ElasticSearchRole(models.Model):
    _inherit = "elasticsearch.role"

    loyalty_program_id = fields.Many2one(
        comodel_name="loyalty.program",
        string="Loyalty Programs",
        readonly=True,
        copy=False,
    )

    _sql_constraints = [
        (
            "loyalty_program_id_group_uniq",
            "UNIQUE(loyalty_program_id, backend_id)",
            _("Only one role by loyalty_program group per backend."),
        )
    ]
