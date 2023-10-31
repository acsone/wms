# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields

from odoo.addons.alc_veterinary_group.models.veterinary_group import VeterinaryGroup
from odoo.addons.elasticsearch_security.models.elasticsearch_role import (
    ElasticSearchRole as ElasticSearchRoleBase,
)


class ElasticSearchRole(ElasticSearchRoleBase):

    vt_group_id = fields.Many2one[VeterinaryGroup](
        string="Veterinary Group",
        readonly=True,
        copy=False,
    )

    _sql_constraints = [
        (
            "vt_group_backend_uniq",
            "UNIQUE(vt_group_id, backend_id)",
            _("Only one role by veterinary group per backend."),
        )
    ]
