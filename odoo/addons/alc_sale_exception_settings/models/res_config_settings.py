# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.models.res_config_settings import (
    ResConfigSettings as SaleSettings,
)


class ResConfigSettings(SaleSettings):

    alc_sale_exception_check_enabled = fields.Boolean(
        string="Sale Exception Check Enabled",
        help="Check this if you want to enable the sale exception checks",
        config_parameter="alc_sale_exception_settings.sale_exception_check_enabled",
    )
