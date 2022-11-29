# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class ElasticSearchRole(models.Model):

    _inherit = "elasticsearch.role"

    vt_group_id = fields.Many2one(
        "veterinary.group", string="Veterinary Group", readonly=True, copy=False,
    )

    _sql_constraints = [
        (
            "vt_group_backend_uniq",
            "UNIQUE(vt_group_id, backend_id)",
            _("Only one role by veterinary group per backend."),
        )
    ]
