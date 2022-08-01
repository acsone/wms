# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ElasticSearchRole(models.Model):

    _inherit = "elasticsearch.role"

    pricelist_id = fields.Many2one(
        "product.pricelist", string="Pricelist", readonly=True, copy=False,
    )

    _sql_constraints = [
        (
            "pl_backend_uniq",
            "UNIQUE(pricelist_id, backend_id)",
            _("Only one role by pricelist per backend."),
        )
    ]
