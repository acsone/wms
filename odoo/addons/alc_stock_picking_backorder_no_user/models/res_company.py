# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.base.models.res_company import Company


class ResCompany(Company):

    no_user_on_backorder = fields.Boolean(
        help="Check this if you want the responsible user to be deleted"
        "from the original picking on the backorder side."
    )
