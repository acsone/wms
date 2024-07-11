# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):

    out_inv_comm_type = fields.Selection(
        selection=[("none", "Free Reference"), ("structured", "Structured Reference")],
        default="structured",
    )
