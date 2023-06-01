# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_company import Company as CompanyBase


class ResCompany(CompanyBase):

    delivered_by_alcyon_constraint = fields.Boolean(
        help="Enable the constaint 'delivered by Alcyon' for pharmacy receptions",
        default=False,
    )
