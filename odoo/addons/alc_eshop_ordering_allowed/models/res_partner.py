# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):

    eshop_ordering_allowed = fields.Boolean(
        help="If not set, this partner is not allowed to pass an order on the eshop.",
        default=True,
    )
