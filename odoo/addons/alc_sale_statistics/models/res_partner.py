# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner as PartnerBase


class ResPartner(PartnerBase):

    ask_sale_statistics = fields.Boolean(
        "Ask for sale statistics ", default=False, index=True
    )
