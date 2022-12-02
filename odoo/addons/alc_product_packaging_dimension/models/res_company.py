# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_company import Company as CompanyBase
from odoo.addons.uom.models.uom_uom import UoM


class ResCompany(CompanyBase):

    packaging_displayed_uom_id = fields.Many2one[UoM](
        help="The unit from which displaying length, width and height in Product Packagings",
        default=lambda self: self.env.ref("uom.product_uom_cm"),
    )
