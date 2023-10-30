# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields

from odoo.addons.elasticsearch_security.models.elasticsearch_role import (
    ElasticSearchRole as ElasticSearchRoleBase,
)
from odoo.addons.product.models.product_pricelist import Pricelist


class ElasticSearchRole(ElasticSearchRoleBase):

    pricelist_id = fields.Many2one[Pricelist](
        string="Pricelist",
        readonly=True,
        copy=False,
    )

    _sql_constraints = [
        (
            "pl_backend_uniq",
            "UNIQUE(pricelist_id, backend_id)",
            _("Only one role by pricelist per backend."),
        )
    ]
