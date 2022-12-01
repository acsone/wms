# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_config import ResConfigSettings as ConfigBase
from odoo.addons.uom.models.uom_uom import UoM


class ResConfigSettings(ConfigBase):

    packaging_displayed_uom_id = fields.Many2one[UoM](
        related="company_id.packaging_displayed_uom_id",
        readonly=False,
    )
