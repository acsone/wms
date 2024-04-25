# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.base.models.res_config import (
    ResConfigSettings as ResConfigSettingsBase,
)


class ResConfigSettings(ResConfigSettingsBase):
    excludes_expired_lot_from_qty_available = fields.Boolean(
        config_parameter="alc_stock_available_product_expiry.excludes_expired_lot_from_qty_available"
    )
